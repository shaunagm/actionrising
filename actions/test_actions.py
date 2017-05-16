import datetime

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.forms.widgets import HiddenInput

from mysite.lib.choices import PrivacyChoices, StatusChoices
from actions.forms import ActionForm
from tags.models import Tag
from profiles import factories as profile_factories


###################
### Test models ###
###################

class TestActionMethods(TestCase):

    def setUp(self):
        self.par = profile_factories.ProfileActionRelationship(action__title="Test Action")
        self.action = self.par.action
        self.buffy = self.action.creator

    def test_get_tags(self):
        tag_one = Tag.objects.create(name="Test Tag One", kind="topic")
        tag_two = Tag.objects.create(name="Test Tag Two", kind="type")
        self.action.tags.add(tag_one)
        self.action.tags.add(tag_two)
        self.assertEqual(list(self.action.get_tags()), [tag_one, tag_two])

    def test_get_creator(self):
        self.assertEqual(self.action.get_visible_creator(), self.buffy)
        self.assertEqual(self.action.get_creator(), self.buffy)
        self.action.anonymize = True
        self.action.save()
        self.assertEqual(self.action.get_visible_creator(), "Anonymous")
        self.assertEqual(self.action.get_creator(), self.buffy)

    def test_get_robust_url(self):
        self.assertEqual(self.action.get_robust_url(), '/actions/action/test-action/')

    def test_is_active(self):
        self.action.status = StatusChoices.ready
        self.action.save()
        self.assertTrue(self.action.is_active())
        self.action.status = StatusChoices.withdrawn
        self.action.save()
        self.assertFalse(self.action.is_active())

    def test_get_days_til_deadline(self):
        self.assertEqual(self.action.get_days_til_deadline(), -1)
        self.action.deadline = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=21)
        self.action.save()
        self.assertEqual(self.action.get_days_til_deadline(), 20)
        self.action.deadline = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        self.action.save()
        self.assertEqual(self.action.get_days_til_deadline(), -1)


class TestActionForms(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")

    def test_action_form_privacy_choices(self):
        initial_form = ActionForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[0][1]
        user_privacy = self.buffy.profile.privacy_defaults.get_global_default_display()
        self.assertEqual(form_inherited_privacy, user_privacy)

    def test_action_form_privacy_choices_when_not_default(self):
        self.buffy.profile.privacy_defaults.global_default = PrivacyChoices.sitewide
        self.buffy.profile.privacy_defaults.save()
        initial_form = ActionForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[3][1]
        # This is an issue with the privacy utils
        self.assertEqual(form_inherited_privacy, "Your Default (Currently 'Visible sitewide')")

    def test_action_status_is_hidden_on_create(self):
        initial_form = ActionForm(user=self.buffy, formtype="create")
        self.assertEqual(type(initial_form.fields['status'].widget), HiddenInput)


class TestActionPrivacy(TestCase):
    def setUp(self):
        super(TestActionPrivacy, self).setUp()
        self.buffy = User.objects.create(username="buffysummers")

    def test_concrete_privacy(self):
        action = self.buffy.action_set.create(privacy=PrivacyChoices.follows)
        self.assertEqual(action.privacy, PrivacyChoices.follows)
        self.assertEqual(action.current_privacy, PrivacyChoices.follows)

    def test_inherit_privacy(self):
        action = self.buffy.action_set.create(privacy=PrivacyChoices.inherit)
        self.assertEqual(action.privacy, PrivacyChoices.inherit)
        self.assertEqual(action.current_privacy, PrivacyChoices.public)

    def test_update_to_inherit_privacy(self):
        action = self.buffy.action_set.create(privacy=PrivacyChoices.follows)
        self.assertEqual(action.privacy, PrivacyChoices.follows)

        action.privacy = PrivacyChoices.inherit
        action.save()

        self.assertEqual(action.privacy, PrivacyChoices.inherit)
        self.assertEqual(action.current_privacy, PrivacyChoices.public)
