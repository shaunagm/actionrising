from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.widgets import HiddenInput
from guardian.shortcuts import assign_perm

from mysite.lib.choices import StatusChoices, PrivacyChoices
from mysite.lib.utils import slugify_helper
from actions.models import Action
from slates.models import Slate
from slates.forms import SlateForm
from slates.templatetags import slate_extras
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
        self.assertEqual(self.slate.get_robust_url(), '/slates/slate/test-slate/')

    def test_is_active(self):
        self.slate.status = StatusChoices.ready
        self.slate.save()
        self.assertTrue(self.slate.is_active())
        self.slate.status = StatusChoices.finished
        self.slate.save()
        self.assertFalse(self.slate.is_active())

    def test_slugify_helper(self):
        self.assertEqual(slugify_helper(Slate, "Test Slate"), "test-slate-1")
        self.assertEqual(slugify_helper(Slate, "Test Different Slate"), "test-different-slate")


class TestSlateViews(TestCase):

    # TODO: add some tests here

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)


class TestSlateForms(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.slate = factories.Slate(title="Test Slate", creator=self.buffy)
        self.giles = User.objects.create(username="giles")

    def test_slate_form_privacy_choices(self):
        initial_form = SlateForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[0][1]
        user_privacy = self.buffy.profile.privacy_defaults.get_global_default_display()
        self.assertEqual(form_inherited_privacy, user_privacy)

    def test_slate_title_is_hidden_on_update_if_not_owner(self):
        update_form = SlateForm(instance=self.slate, user=self.buffy, formtype="update")
        self.assertNotEqual(type(update_form.fields['title'].widget), HiddenInput)
        update_form = SlateForm(instance=self.slate, user=self.giles, formtype="update")
        self.assertEqual(type(update_form.fields['title'].widget), HiddenInput)


class TestSlateTemplateTags(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.slate = factories.Slate(title="Test Slate", creator=self.buffy)
        self.giles = User.objects.create(username="giles")
        class Request(object):
            user = self.buffy
        self.mockRequest = Request()

    def test_check_can_edit(self):
        # Test owner
        context = {'request': self.mockRequest }
        can_edit = slate_extras.check_can_edit(context, self.slate)
        self.assertTrue(can_edit)
        # Test non-owner
        context['request'].user = self.giles
        can_edit = slate_extras.check_can_edit(context, self.slate)
        self.assertFalse(can_edit)
        # Add non-owner as admin
        assign_perm('administer_slate', self.giles, self.slate)
        can_edit = slate_extras.check_can_edit(context, self.slate)
        self.assertTrue(can_edit)


class TestSlatePrivacy(TestCase):
    def setUp(self):
        super(TestSlatePrivacy, self).setUp()
        self.buffy = User.objects.create(username="buffysummers")

    def test_concrete_privacy(self):
        slate = self.buffy.slate_set.create(privacy=PrivacyChoices.follows)
        self.assertEqual(slate.privacy, PrivacyChoices.follows)
        self.assertEqual(slate.current_privacy, PrivacyChoices.follows)

    def test_inherit_privacy(self):
        slate = self.buffy.slate_set.create(privacy=PrivacyChoices.inherit)
        self.assertEqual(slate.privacy, PrivacyChoices.inherit)
        self.assertEqual(slate.current_privacy, PrivacyChoices.public)

    def test_update_to_inherit_privacy(self):
        slate = self.buffy.slate_set.create(privacy=PrivacyChoices.follows)
        self.assertEqual(slate.privacy, PrivacyChoices.follows)

        slate.privacy = PrivacyChoices.inherit
        slate.save()

        self.assertEqual(slate.privacy, PrivacyChoices.inherit)
        self.assertEqual(slate.current_privacy, PrivacyChoices.public)


class TestCreateSlate(TestCase):
    def setUp(self):
        super(TestCreateSlate, self).setUp()
        self.buffy = User.objects.create(username="buffysummers")

    def test_create_slate(self):
        self.client.force_login(self.buffy)
        resp = self.client.post(reverse("create_slate"), {
            'title': "My new slate",
            'description': "It's gonna be good",
            'status': StatusChoices.ready,
            'privacy': PrivacyChoices.follows,
            'actions': [],
        })

        self.assertEqual(resp.status_code, 302)
        slate = Slate.objects.get()
        self.assertRedirects(resp, slate.get_robust_url())

        self.assertEqual(slate.privacy, PrivacyChoices.follows)
