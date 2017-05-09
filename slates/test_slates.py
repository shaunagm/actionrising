from django.test import TestCase
from django.contrib.auth.models import User

from mysite.lib.choices import StatusChoices
from mysite.lib.utils import slugify_helper
from actions.models import Action
from slates.models import Slate
from slates.forms import SlateForm
from . import factories


class TestSlateMethods(TestCase):

    def setUp(self):
        self.sar = factories.SlateActionRelationship(
            slate__title="Test Slate",
            action__title="Test Action")
        self.action = self.sar.action
        self.slate = self.sar.slate

    def test_get_sar_given_action(self):
        sar = self.slate.get_sar_given_action(self.action)
        self.assertEqual(sar.slate, self.slate)
        self.assertEqual(sar.action, self.action)
        self.assertEqual(sar.pk, self.sar.pk)

    def test_get_robust_url(self):
        self.assertEqual(self.slate.get_robust_url(), '/slates/slate/test-slate')

    def test_is_active(self):
        self.slate.status = StatusChoices.ready
        self.slate.save()
        self.assertTrue(self.slate.is_active())
        self.slate.status = StatusChoices.finished
        self.slate.save()
        self.assertFalse(self.slate.is_active())

    def test_slugify_helper(self):
        self.assertEqual(slugify_helper(Slate, "Test Slate"), "test-slate0")
        self.assertEqual(slugify_helper(Slate, "Test Different Slate"), "test-different-slate")


class TestSlateViews(TestCase):

    # TODO: add some tests here

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)


class TestSlateForms(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")

    def test_slate_form_privacy_choices(self):
        initial_form = SlateForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[0][1]
        user_privacy = self.buffy.profile.privacy_defaults.get_global_default_display()
        self.assertEqual(form_inherited_privacy, user_privacy)
