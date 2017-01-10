import datetime, mock

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from profiles.models import Profile, ProfileActionRelationship

from actions.models import (Action, Slate, ActionTopic, ActionType, SlateActionRelationship,
    slugify_helper)
from actions.lib import act_location
from actions.views import create_action_helper, create_slate_helper, edit_slate_helper
from actions.forms import ActionForm, SlateForm


###################
### Test models ###
###################

class TestActionMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.topic = ActionTopic.objects.create(name="Test Topic")
        self.actiontype = ActionType.objects.create(name="Test ActionType")
        self.slate = Slate.objects.create(title="Test Slate", creator=self.buffy)
        self.sar = SlateActionRelationship.objects.create(slate=self.slate, action=self.action)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)

    def test_get_tags(self):
        self.action.topics.add(self.topic)
        self.action.actiontypes.add(self.actiontype)
        self.assertEqual(self.action.get_tags(), [self.topic, self.actiontype])

    def test_get_creator(self):
        self.assertEqual(self.action.get_creator(), self.buffy)
        self.action.anonymize = True
        self.action.save()
        self.assertEqual(self.action.get_creator(), "Anonymous")

    def test_get_robust_url(self):
        self.assertEqual(self.action.get_robust_url(), '/actions/action/test-action')
        self.assertEqual(self.slate.get_robust_url(), '/actions/slate/test-slate')

    def test_get_sar_given_action(self):
        sar = self.slate.get_sar_given_action(self.action)
        self.assertEqual(sar.slate, self.slate)
        self.assertEqual(sar.action, self.action)
        self.assertEqual(sar.pk, self.sar.pk)

    def test_is_active(self):
        self.slate.status = 'rea'
        self.slate.save()
        self.action.status = 'rea'
        self.action.save()
        self.assertTrue(self.action.is_active())
        self.assertTrue(self.slate.is_active())
        self.slate.status = 'fin'
        self.slate.save()
        self.action.status = 'wit'
        self.action.save()
        self.assertFalse(self.action.is_active())
        self.assertFalse(self.slate.is_active())

    def test_slugify_helper(self):
        self.assertEqual(slugify_helper(Action, "Test Action"), "test-action0")
        self.assertEqual(slugify_helper(Action, "Test Different Action"), "test-different-action")
        self.assertEqual(slugify_helper(ActionType, "Test ActionType"), "test-actiontype0")
        self.assertEqual(slugify_helper(ActionType, "Test Different ActionType"), "test-different-actiontype")
        self.assertEqual(slugify_helper(Slate, "Test Slate"), "test-slate0")
        self.assertEqual(slugify_helper(Slate, "Test Different Slate"), "test-different-slate")

    def test_get_days_til_deadline(self):
        self.assertEqual(self.action.get_days_til_deadline(), -1)
        self.action.deadline = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=21)
        self.action.save()
        self.assertEqual(self.action.get_days_til_deadline(), 20)
        self.action.deadline = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        self.action.save()
        self.assertEqual(self.action.get_days_til_deadline(), -1)


class TestActionViews(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.topic = ActionTopic.objects.create(name="Test Topic")
        self.actiontype = ActionType.objects.create(name="Test ActionType")

    def test_create_action_helper(self):
        with self.assertRaises(ObjectDoesNotExist):
            Action.objects.get(title="Test title")
        obj = Action(title="Test title")
        obj = create_action_helper(obj, [self.actiontype], [self.topic], self.buffy)
        self.assertEqual(obj.creator, self.buffy)
        self.assertEqual(obj.get_tags(), [self.topic, self.actiontype])

    def test_create_slate_helper(self):
        with self.assertRaises(ObjectDoesNotExist):
            Slate.objects.get(title="Test title")
        obj = Slate(title="Test title")
        obj = create_slate_helper(obj, [self.action], self.buffy)
        self.assertEqual(obj.creator, self.buffy)
        self.assertEqual(list(obj.actions.all()), [self.action])

    def test_edit_slate_helper(self):
        # No actions when create
        obj = Slate.objects.create(title="Test title", creator=self.buffy)
        self.assertEqual(list(obj.actions.all()), [])
        # Add some actions via edit_slate_helper
        edit_slate_helper(obj, [self.action])
        self.assertEqual(list(obj.actions.all()), [self.action])
        # Create a new action, and then swap out the actions on the slate
        new_action = Action.objects.create(title="New action", creator=self.buffy)
        edit_slate_helper(obj, [new_action])
        self.assertEqual(list(obj.actions.all()), [new_action])

class TestActionForms(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")

    def test_action_form_privacy_choices(self):
        initial_form = ActionForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[0][1]
        user_privacy = self.buffy.profile.privacy_defaults.get_global_default_display()
        self.assertEqual(form_inherited_privacy, user_privacy)

    def test_action_form_privacy_choices_when_not_default(self):
        self.buffy.profile.privacy_defaults.global_default = "sit"
        self.buffy.profile.privacy_defaults.save()
        initial_form = ActionForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[3][1]
        # This is an issue with the privacy utils
        self.assertEqual(form_inherited_privacy, "Your Default (Currently 'Visible Sitewide')")

    def test_action_status_is_hidden_on_create(self):
        from django.forms.widgets import HiddenInput
        initial_form = ActionForm(user=self.buffy, formtype="create")
        self.assertEqual(type(initial_form.fields['status'].widget), HiddenInput)

    def test_slate_form_privacy_choices(self):
        initial_form = SlateForm(user=self.buffy)
        form_inherited_privacy = initial_form.fields['privacy'].choices[0][1]
        user_privacy = self.buffy.profile.privacy_defaults.get_global_default_display()
        self.assertEqual(form_inherited_privacy, user_privacy)

class TestLocation(TestCase):

    def setUp(self):
        self.testing_user = User.objects.create(username="testing_user")
        self.action = Action.objects.create(title="Test Action with Location", creator=self.testing_user)

    @mock.patch('actions.lib.act_location.geocode')
    @mock.patch('actions.lib.act_location.find_congressional_district')
    def test_populate_location_and_district(self, find_congressional_district, geocode):

        geocoded_location = mock.MagicMock()
        geocoded_location.latitude = 0.0
        geocoded_location.longitude = 0.0
        geocode.return_value = geocoded_location

        find_congressional_district - mock.MagicMock()
        find_congressional_district.return_value = {"state":"MA","district":5}

        act_location.populate_location_and_district(self.action)

        self.assertEqual(self.action.lat, 0.0)
        self.assertEqual(self.action.lon, 0.0)
        self.assertEqual(self.action.state, "MA")
        self.assertEqual(self.action.district, "MA-5")
