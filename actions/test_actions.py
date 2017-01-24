import datetime, mock

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from profiles.models import Profile, ProfileActionRelationship

from mysite.lib.utils import slugify_helper
from actions.models import Action
from actions.forms import ActionForm
from tags.models import Tag


###################
### Test models ###
###################

class TestActionMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.tag_one = Tag.objects.create(name="Test Tag One", kind="topic")
        self.tag_two = Tag.objects.create(name="Test Tag Two", kind="type")
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)

    def test_get_tags(self):
        self.action.tags.add(self.tag_one)
        self.action.tags.add(self.tag_two)
        self.assertEqual(list(self.action.get_tags()), [self.tag_one, self.tag_two])

    def test_get_creator(self):
        self.assertEqual(self.action.get_creator(), self.buffy)
        self.action.anonymize = True
        self.action.save()
        self.assertEqual(self.action.get_creator(), "Anonymous")

    def test_get_robust_url(self):
        self.assertEqual(self.action.get_robust_url(), '/actions/action/test-action')

    def test_is_active(self):
        self.action.status = 'rea'
        self.action.save()
        self.assertTrue(self.action.is_active())
        self.action.status = 'wit'
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
