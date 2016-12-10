from django.test import TestCase

from django.contrib.auth.models import User, AnonymousUser
from actions.models import Action, Slate, SlateActionRelationship
from profiles.models import Profile, ProfileActionRelationship

from mysite.utils import check_for_ownership, get_global_privacy_default, check_privacy

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
        # No one "owns" a PAR
        self.assertFalse(check_for_ownership(self.par, self.buffy))
        self.assertFalse(check_for_ownership(self.par, self.faith))
        self.assertFalse(check_for_ownership(self.par, self.anon))

    def test_check_for_ownership_sar(self):
        # No one "owns" an SAR
        self.assertFalse(check_for_ownership(self.sar, self.buffy))
        self.assertFalse(check_for_ownership(self.sar, self.faith))
        self.assertFalse(check_for_ownership(self.sar, self.anon))

    def test_get_global_privacy_default_when_unchanged(self):
        self.assertEqual(get_global_privacy_default(self.faith.profile), "sit")
        self.assertEqual(get_global_privacy_default(self.action), "sit")
        self.assertEqual(get_global_privacy_default(self.slate), "sit")
        self.assertEqual(get_global_privacy_default(self.par), "sit")
        self.assertEqual(get_global_privacy_default(self.sar), "sit")

    def test_get_global_privacy_default_when_changed(self):
        self.faith.profile.privacy_defaults.global_default = "pub"
        self.faith.profile.privacy_defaults.save()
        self.assertEqual(get_global_privacy_default(self.faith.profile), "pub")
        self.assertEqual(get_global_privacy_default(self.action), "pub")
        self.assertEqual(get_global_privacy_default(self.slate), "pub")
        self.assertEqual(get_global_privacy_default(self.par), "pub")
        self.assertEqual(get_global_privacy_default(self.sar), "pub")

    def test_check_privacy_of_action(self):
        # The global default is sitewide, so before changes, Buffy should have access
        # and Anon should not
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertFalse(check_privacy(self.action, self.anon))
        # Now we set the global default to pub and everyone can access
        self.faith.profile.privacy_defaults.global_default = "pub"
        self.faith.profile.privacy_defaults.save()
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertTrue(check_privacy(self.action, self.anon))
        # Now let's make access more restrictive on the individual objects
        self.action.privacy = "sit"
        self.action.save()
        self.assertTrue(check_privacy(self.action, self.buffy))
        self.assertFalse(check_privacy(self.action, self.anon))
        # And let's just check that the actual fields are what we expect, because why not
        self.assertEqual([self.faith.profile.privacy_defaults.global_default, self.action.privacy],
            ["pub", "sit"])

    def test_check_privacy_of_par(self):
        # PAR privacy is set to the profile's privacy.  The global default is sitewide,
        # so before changes, Buffy should have access and Anon should not
        # TODO: soon PAR privacy will be set to the more restrictive of Action or Profile,
        # update the tests then
        self.assertTrue(check_privacy(self.par.profile, self.buffy))
        self.assertFalse(check_privacy(self.par.profile, self.anon))
        # Now we set the global default to pub and everyone can access
        self.faith.profile.privacy_defaults.global_default = "pub"
        self.faith.profile.privacy_defaults.save()
        self.assertTrue(check_privacy(self.par.profile, self.buffy))
        self.assertTrue(check_privacy(self.par.profile, self.anon))

    def test_check_privacy_of_sar(self):
        # SAR privacy is set to the slate's privacy.  The global default is sitewide,
        # so before changes, Buffy should have access and Anon should not.
        # TODO: soon SAR privacy will be set to the more restrictive of Action or Slate,
        # update the tests then
        self.assertTrue(check_privacy(self.sar.slate, self.buffy))
        self.assertFalse(check_privacy(self.sar.slate, self.anon))
        # Now we set the global default to pub and everyone can access
        self.faith.profile.privacy_defaults.global_default = "pub"
        self.faith.profile.privacy_defaults.save()
        self.assertTrue(check_privacy(self.sar.slate, self.buffy))
        self.assertTrue(check_privacy(self.sar.slate, self.anon))
