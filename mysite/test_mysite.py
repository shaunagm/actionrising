from django.test import TestCase

from django.contrib.auth.models import User, AnonymousUser
from actions.models import Action, Slate, SlateActionRelationship
from profiles.models import Profile, ProfileActionRelationship

from mysite.lib.privacy import (check_for_ownership, get_global_privacy_default,
    check_privacy)

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

    def test_check_for_ownership_profile(self):
        self.assertFalse(check_for_ownership(self.faith.profile, self.buffy))
        self.assertTrue(check_for_ownership(self.faith.profile, self.faith))
        self.assertFalse(check_for_ownership(self.faith.profile, self.anon))

    def test_check_for_ownership_action(self):
        self.assertFalse(check_for_ownership(self.action, self.buffy))
        self.assertTrue(check_for_ownership(self.action, self.faith))
        self.assertFalse(check_for_ownership(self.action, self.anon))

    def test_check_for_ownership_slate(self):
        self.assertFalse(check_for_ownership(self.slate, self.buffy))
        self.assertTrue(check_for_ownership(self.slate, self.faith))
        self.assertFalse(check_for_ownership(self.slate, self.anon))

    def test_check_for_ownership_par(self):
        # The owner of the profile in the PAR 'owns' the PAR
        self.assertFalse(check_for_ownership(self.par, self.buffy))
        self.assertTrue(check_for_ownership(self.par, self.faith))
        self.assertFalse(check_for_ownership(self.par, self.anon))

    def test_check_for_ownership_sar(self):
        # The creator of the slate 'owns' the SAR
        self.assertFalse(check_for_ownership(self.sar, self.buffy))
        self.assertTrue(check_for_ownership(self.sar, self.faith))
        self.assertFalse(check_for_ownership(self.sar, self.anon))

    def test_get_global_privacy_default_when_unchanged(self):
        self.assertEqual(get_global_privacy_default(self.faith.profile), "pub")
        self.assertEqual(get_global_privacy_default(self.action), "pub")
        self.assertEqual(get_global_privacy_default(self.slate), "pub")
        self.assertEqual(get_global_privacy_default(self.par), "pub")
        self.assertEqual(get_global_privacy_default(self.sar), "pub")

    def test_get_global_privacy_default_when_changed(self):
        self.faith.profile.privacy_defaults.global_default = "pub"
        self.faith.profile.privacy_defaults.save()
        self.assertEqual(get_global_privacy_default(self.faith.profile), "pub")
        self.assertEqual(get_global_privacy_default(self.action), "pub")
        self.assertEqual(get_global_privacy_default(self.slate), "pub")
        self.assertEqual(get_global_privacy_default(self.par), "pub")
        self.assertEqual(get_global_privacy_default(self.sar), "pub")

    def test_check_privacy_of_action(self):
        # The global default is public, so before changes, Buffy & anon should have access
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertTrue(check_privacy(self.action, self.anon))
        # Now we set the global default to pub and everyone can access
        self.faith.profile.privacy_defaults.global_default = "sit"
        self.faith.profile.privacy_defaults.save()
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertFalse(check_privacy(self.action, self.anon))
        # Now let's make access more open on the individual objects
        self.action.privacy = "pub"
        self.action.save()
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertTrue(check_privacy(self.action, self.anon))
        # And let's just check that the actual fields are what we expect, because why not
        self.assertEqual([self.faith.profile.privacy_defaults.global_default, self.action.privacy],
            ["sit", "pub"])

    def test_check_privacy_of_par(self):
        # PAR privacy is set to the more restrictive of Action or Profile
        # Global default is public, so before changes, Buffy & Anon should both have access
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertTrue(check_privacy(self.par, self.anon))
        # Now we set the global default to sit and only Buffy can access
        self.faith.profile.privacy_defaults.global_default = "sit"
        self.faith.profile.privacy_defaults.save()
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertFalse(check_privacy(self.par, self.anon))
        # If we change action to public and profile to sit, only Buffy can access
        self.par.profile.privacy = "sit"
        self.par.profile.save()
        self.par.action.privacy = "pub"
        self.par.action.save()
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertFalse(check_privacy(self.par, self.anon))
        # If we change action to sit and profile to public, only Buffy can access
        self.par.profile.privacy = "pub"
        self.par.profile.save()
        self.par.action.privacy = "sit"
        self.par.action.save()
        self.assertTrue(check_privacy(self.par, self.buffy))
        self.assertFalse(check_privacy(self.par, self.anon))

    def test_check_privacy_of_sar(self):
        # SAR privacy is set to the more restrictive of Action or Slate
        # Global default is public, so before changes, Buffy & Anon should both have access
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertTrue(check_privacy(self.sar, self.anon))
        # Now we set the global default to sit and only Buffy can access
        self.faith.profile.privacy_defaults.global_default = "sit"
        self.faith.profile.privacy_defaults.save()
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertFalse(check_privacy(self.sar, self.anon))
        # If we change action to public and slate to sit, only Buffy can access
        self.sar.slate.privacy = "sit"
        self.sar.slate.save()
        self.sar.action.privacy = "pub"
        self.sar.action.save()
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertFalse(check_privacy(self.sar, self.anon))
        # If we change action to sit and slate to public, only Buffy can access
        self.sar.slate.privacy = "pub"
        self.sar.slate.save()
        self.sar.action.privacy = "sit"
        self.sar.action.save()
        self.assertTrue(check_privacy(self.sar, self.buffy))
        self.assertFalse(check_privacy(self.sar, self.anon))
