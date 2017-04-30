from django.test import TestCase

from django.contrib.auth.models import User, AnonymousUser
from actions.models import Action
from slates.models import Slate, SlateActionRelationship
from profiles.models import Profile, ProfileActionRelationship
from tags.models import Tag

from mysite.lib.utils import slugify_helper
from mysite.lib.choices import PrivacyChoices
from mysite.lib.privacy import check_privacy, get_global_privacy_default

##################
### Test utils ###
##################

class TestPrivacyUtils(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.anon = AnonymousUser()
        self.action = Action.objects.create(slug="test-action", creator=self.faith)
        self.slate = Slate.objects.create(slug="test-slate", creator=self.faith)
        self.par = ProfileActionRelationship(profile=self.faith.profile, action=self.action)
        self.sar = SlateActionRelationship(slate=self.slate, action=self.action)

    def test_get_global_privacy_default_when_unchanged(self):
        self.assertEqual(get_global_privacy_default(self.faith.profile), PrivacyChoices.public)
        self.assertEqual(get_global_privacy_default(self.action), PrivacyChoices.public)
        self.assertEqual(get_global_privacy_default(self.slate), PrivacyChoices.public)
        self.assertEqual(get_global_privacy_default(self.par), PrivacyChoices.public)
        self.assertEqual(get_global_privacy_default(self.sar), PrivacyChoices.public)

    def test_get_global_privacy_default_when_changed(self):
        self.buffy.profile.privacy_defaults.global_default = PrivacyChoices.public
        self.buffy.profile.privacy_defaults.save()
        self.faith.profile.privacy_defaults.global_default = PrivacyChoices.sitewide
        self.faith.profile.privacy_defaults.save()
        self.assertEqual(get_global_privacy_default(self.faith.profile), PrivacyChoices.sitewide)
        self.assertEqual(get_global_privacy_default(self.buffy.profile), PrivacyChoices.public)
        self.assertEqual(get_global_privacy_default(self.action), PrivacyChoices.sitewide)
        self.assertEqual(get_global_privacy_default(self.slate), PrivacyChoices.sitewide)
        self.assertEqual(get_global_privacy_default(self.par), PrivacyChoices.sitewide)
        self.assertEqual(get_global_privacy_default(self.sar), PrivacyChoices.sitewide)

    def test_check_privacy_of_action(self):
        # The global default is public, so before changes, Buffy & anon should have access
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertTrue(check_privacy(self.action, self.anon))
        # Now we set the global default to sitewide
        self.faith.profile.privacy_defaults.global_default = PrivacyChoices.sitewide
        self.faith.profile.privacy_defaults.save()
        self.action.refresh_current_privacy() #TODO is this called appropriately in the codebase?
        self.assertEqual(self.action.current_privacy, PrivacyChoices.sitewide)
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertFalse(check_privacy(self.action, self.anon))
        # Now let's make access more open on the individual objects
        self.action.privacy = PrivacyChoices.public
        self.action.save()
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertTrue(check_privacy(self.action, self.anon))
        # And let's just check that the actual fields are what we expect, because why not
        self.assertEqual([self.faith.profile.privacy_defaults.global_default, self.action.privacy],
            [PrivacyChoices.sitewide, PrivacyChoices.public])

    def test_check_privacy_of_par(self):
        # PAR privacy is set to the more restrictive of Action or Profile
        # Global default is public, so before changes, Buffy & Anon should both have access
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertTrue(check_privacy(self.par, self.anon))
        # Now we set the global default to sitewide and only Buffy can access
        self.faith.profile.privacy_defaults.global_default = PrivacyChoices.sitewide
        self.faith.profile.privacy_defaults.save()
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertFalse(check_privacy(self.par, self.anon))
        # If we change action to public and profile to sitewide, only Buffy can access
        self.par.profile.privacy = PrivacyChoices.sitewide
        self.par.profile.save()
        self.par.action.privacy = PrivacyChoices.public
        self.par.action.save()
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertFalse(check_privacy(self.par, self.anon))
        # If we change action to sitewide and profile to public, only Buffy can access
        self.par.profile.privacy = PrivacyChoices.public
        self.par.profile.save()
        self.par.action.privacy = PrivacyChoices.sitewide
        self.par.action.save()
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertFalse(check_privacy(self.par, self.anon))

    def test_check_privacy_of_sar(self):
        # SAR privacy is set to the more restrictive of Action or Slate
        # Global default is public, so before changes, Buffy & Anon should both have access
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertTrue(check_privacy(self.sar, self.anon))
        # Now we set the global default to sitewide and only Buffy can access
        self.faith.profile.privacy_defaults.global_default = PrivacyChoices.sitewide
        self.faith.profile.privacy_defaults.save()
        self.faith.profile.save_dependencies()
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertFalse(check_privacy(self.sar, self.anon))
        # If we change action to public and slate to sitewide, only Buffy can access
        self.sar.slate.privacy = PrivacyChoices.sitewide
        self.sar.slate.save()
        self.sar.action.privacy = PrivacyChoices.public
        self.sar.action.save()
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertFalse(check_privacy(self.sar, self.anon))
        # If we change action to sitewide and slate to public, only Buffy can access
        self.sar.slate.privacy = PrivacyChoices.public
        self.sar.slate.save()
        self.sar.action.privacy = PrivacyChoices.sitewide
        self.sar.action.save()
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertFalse(check_privacy(self.sar, self.anon))

class TestMiscUtils(TestCase):

    def test_slugify_helper(self):
        self.assertEqual(slugify_helper(Action, "Test Action"), "test-action")
        self.assertEqual(slugify_helper(Action, "Test Different Action"), "test-different-action")
        self.assertEqual(slugify_helper(Slate, "Test Slate"), "test-slate")
        self.assertEqual(slugify_helper(Slate, "Test Different Slate"), "test-different-slate")
        self.assertEqual(slugify_helper(Tag, "Test Tag"), "test-tag")
        self.assertEqual(slugify_helper(Tag, "Test Different Tag"), "test-different-tag")
