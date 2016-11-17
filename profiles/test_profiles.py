from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from actions.models import Action
from profiles.models import Profile, Relationship, ProfileActionRelationship
from profiles.templatetags.profile_extras import get_friendslist, get_relationship
from profiles.views import toggle_relationships_helper, toggle_par_helper, manage_action_helper

###################
### Test models ###
###################

class TestProfileMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.relationship = Relationship.objects.create(person_A=self.buffy.profile,
            person_B=self.faith.profile)
        self.lorne = User.objects.create(username="lorne") # Relationshipless

    def test_get_relationship_given_profile(self):
        relationship = self.buffy.profile.get_relationship_given_profile(self.faith.profile)
        self.assertEqual(relationship, self.relationship)

    def test_get_relationship_given_own_profile(self):
        relationship = self.buffy.profile.get_relationship_given_profile(self.buffy.profile)
        self.assertIsNone(relationship)

    def test_get_relationship_given_profile_when_no_relationship_exists(self):
        relationship = self.buffy.profile.get_relationship_given_profile(self.lorne.profile)
        self.assertIsNone(relationship)

    def test_get_followers(self):
        self.relationship.B_follows_A = True
        self.relationship.save()
        self.assertEqual(list(self.buffy.profile.get_followers()), [self.faith.profile])
        self.assertEqual(list(self.faith.profile.get_followers()), [])
        self.assertEqual(list(self.lorne.profile.get_followers()), [])

class TestRelationshipMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.relationship = Relationship.objects.create(person_A=self.buffy.profile,
            person_B=self.faith.profile)
        self.lorne = User.objects.create(username="lorne") # Relationshipless

    def test_get_other(self):
        self.assertEqual(self.relationship.get_other(self.buffy.profile), self.faith.profile)
        self.assertEqual(self.relationship.get_other(self.faith.profile), self.buffy.profile)
        self.assertIsNone(self.relationship.get_other(self.lorne.profile))

    def test_target_follows_current_profile(self):
        self.relationship.B_follows_A = True
        self.relationship.save()
        self.assertTrue(self.relationship.target_follows_current_profile(self.buffy.profile))
        self.assertFalse(self.relationship.target_follows_current_profile(self.faith.profile))
        self.assertIsNone(self.relationship.target_follows_current_profile(self.lorne.profile))

    def test_current_profile_follows_target(self):
        self.relationship.B_follows_A = True
        self.relationship.save()
        self.assertFalse(self.relationship.current_profile_follows_target(self.buffy.profile))
        self.assertTrue(self.relationship.current_profile_follows_target(self.faith.profile))
        self.assertIsNone(self.relationship.current_profile_follows_target(self.lorne.profile))

    def test_target_accountable_to_current_profile(self):
        self.relationship.B_accountable_A = True
        self.relationship.save()
        self.assertTrue(self.relationship.target_accountable_to_current_profile(self.buffy.profile))
        self.assertFalse(self.relationship.target_accountable_to_current_profile(self.faith.profile))
        self.assertIsNone(self.relationship.target_accountable_to_current_profile(self.lorne.profile))

    def test_current_profile_accountable_to_target(self):
        self.relationship.B_accountable_A = True
        self.relationship.save()
        self.assertFalse(self.relationship.current_profile_accountable_to_target(self.buffy.profile))
        self.assertTrue(self.relationship.current_profile_accountable_to_target(self.faith.profile))
        self.assertIsNone(self.relationship.current_profile_accountable_to_target(self.lorne.profile))

    def test_target_mutes_current_profile(self):
        self.relationship.B_mutes_A = True
        self.relationship.save()
        self.assertTrue(self.relationship.target_mutes_current_profile(self.buffy.profile))
        self.assertFalse(self.relationship.target_mutes_current_profile(self.faith.profile))
        self.assertIsNone(self.relationship.target_mutes_current_profile(self.lorne.profile))

    def test_current_profile_accountable_to_target(self):
        self.relationship.B_mutes_A = True
        self.relationship.save()
        self.assertFalse(self.relationship.current_profile_mutes_target(self.buffy.profile))
        self.assertTrue(self.relationship.current_profile_mutes_target(self.faith.profile))
        self.assertIsNone(self.relationship.current_profile_mutes_target(self.lorne.profile))

    def test_toggle_following_for_current_profile(self):
        # Starting with A (Buffy) not following B (Faith)
        self.assertFalse(self.relationship.A_follows_B)
        # Toggle returns the new status, which is True - Buffy does now follow Faith
        self.assertTrue(self.relationship.toggle_following_for_current_profile(self.buffy.profile))
        # Confirm A now follows B
        self.assertTrue(self.relationship.A_follows_B)
        # Confirm B does not follow A
        self.assertFalse(self.relationship.B_follows_A)
        # Toggle back to not following
        self.assertFalse(self.relationship.toggle_following_for_current_profile(self.buffy.profile))
        # Toggle the other direction - B (Faith) following A (Buffy)
        self.assertTrue(self.relationship.toggle_following_for_current_profile(self.faith.profile))
        # Toggling in one direction should not effect the other direction
        self.assertTrue(self.relationship.toggle_following_for_current_profile(self.buffy.profile))
        # Trying to toggle someone not part of the relationship should return none
        self.assertIsNone(self.relationship.toggle_following_for_current_profile(self.lorne.profile))

    def test_toggle_accountability_for_current_profile(self):
        # This is essentially test_toggle_following_for_current_profile with method and var names changed
        self.assertFalse(self.relationship.A_accountable_B)
        self.assertTrue(self.relationship.toggle_accountability_for_current_profile(self.buffy.profile))
        self.assertTrue(self.relationship.A_accountable_B)
        self.assertFalse(self.relationship.B_accountable_A)
        self.assertFalse(self.relationship.toggle_accountability_for_current_profile(self.buffy.profile))
        self.assertTrue(self.relationship.toggle_accountability_for_current_profile(self.faith.profile))
        self.assertTrue(self.relationship.toggle_accountability_for_current_profile(self.buffy.profile))
        self.assertIsNone(self.relationship.toggle_accountability_for_current_profile(self.lorne.profile))

    def test_toggle_mute_for_current_profile(self):
        # This is essentially test_toggle_following_for_current_profile with method and var names changed
        self.assertFalse(self.relationship.A_mutes_B)
        self.assertTrue(self.relationship.toggle_mute_for_current_profile(self.buffy.profile))
        self.assertTrue(self.relationship.A_mutes_B)
        self.assertFalse(self.relationship.B_mutes_A)
        self.assertFalse(self.relationship.toggle_mute_for_current_profile(self.buffy.profile))
        self.assertTrue(self.relationship.toggle_mute_for_current_profile(self.faith.profile))
        self.assertTrue(self.relationship.toggle_mute_for_current_profile(self.buffy.profile))
        self.assertIsNone(self.relationship.toggle_mute_for_current_profile(self.lorne.profile))

###########################
### Test view functions ###
###########################

# The views themselves will be covered via integration tests, but we can test the helper functions

class TestToggleRelationshipsView(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.relationship = Relationship.objects.create(person_A=self.buffy.profile,
            person_B=self.faith.profile)
        self.lorne = User.objects.create(username="lorne")

    def test_toggle_creates_relationsip(self):
        with self.assertRaises(ObjectDoesNotExist):
            Relationship.objects.get(person_A=self.buffy.profile, person_B=self.lorne.profile)
        toggle_relationships_helper("follow", self.buffy.profile, self.lorne.profile)
        relationship = Relationship.objects.get(person_A=self.buffy.profile, person_B=self.lorne.profile)
        self.assertTrue(relationship.A_follows_B)

    def test_toggle_follow(self):
        self.assertFalse(self.relationship.A_follows_B)
        status = toggle_relationships_helper("follow", self.buffy.profile, self.faith.profile)
        self.assertTrue(status)
        relationship = Relationship.objects.get(person_A=self.buffy.profile, person_B=self.faith.profile)
        self.assertTrue(relationship.A_follows_B)

    def test_toggle_twice(self):
        self.assertFalse(self.relationship.A_follows_B)
        status = toggle_relationships_helper("follow", self.buffy.profile, self.faith.profile)
        self.assertTrue(status)
        status = toggle_relationships_helper("follow", self.buffy.profile, self.faith.profile)
        self.assertFalse(status)
        relationship = Relationship.objects.get(person_A=self.buffy.profile, person_B=self.faith.profile)
        self.assertFalse(relationship.A_follows_B)

    def test_toggle_mute(self):
        self.assertFalse(self.relationship.A_mutes_B)
        status = toggle_relationships_helper("mute", self.buffy.profile, self.faith.profile)
        self.assertTrue(status)
        relationship = Relationship.objects.get(person_A=self.buffy.profile, person_B=self.faith.profile)
        self.assertTrue(relationship.A_mutes_B)

    def test_toggle_account(self):
        self.assertFalse(self.relationship.A_accountable_B)
        status = toggle_relationships_helper("account", self.buffy.profile, self.faith.profile)
        self.assertTrue(status)
        relationship = Relationship.objects.get(person_A=self.buffy.profile, person_B=self.faith.profile)
        self.assertTrue(relationship.A_accountable_B)

class TestProfileActionRelationshipView(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(slug="test-action", creator=self.faith)

    def test_par_helper_add(self):
        toggle_par_helper("add", self.buffy.profile, self.action)
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(par.status, "ace")

    def test_par_helper_remove(self):
        toggle_par_helper("add", self.buffy.profile, self.action)
        toggle_par_helper("remove", self.buffy.profile, self.action)
        with self.assertRaises(ObjectDoesNotExist):
            ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)

class TestManageActionView(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.lorne = User.objects.create(username="lorne")
        self.action = Action.objects.create(slug="test-action", creator=self.faith)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)
        class MockForm(object):
            cleaned_data = {'priority': 'hig', 'status': 'rea', 'privacy': 'pub',
                'profiles': [self.lorne.profile]}
        self.mock_form = MockForm()

    def test_changes_fields_from_defaults(self):
        self.assertEqual([self.par.priority, self.par.privacy, self.par.status], ["med", "inh", "inh"])
        manage_action_helper(self.par, self.mock_form)
        self.assertEqual([self.par.priority, self.par.privacy, self.par.status], ["hig", "pub", "rea"])

    def test_make_new_par_for_profile(self):
        with self.assertRaises(ObjectDoesNotExist):
            ProfileActionRelationship.objects.get(profile=self.lorne.profile, action=self.action)
        manage_action_helper(self.par, self.mock_form)
        par = ProfileActionRelationship.objects.get(profile=self.lorne.profile, action=self.action)
        self.assertEqual(par.profile.user, self.lorne)

#########################
### Test templatetags ###
#########################

class TestProfileExtras(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.relationship = Relationship.objects.create(person_A=self.buffy.profile,
            person_B=self.faith.profile)
        class MockRequest(object):
            user = self.buffy
        self.context = {'request': MockRequest()}

    def test_get_friendslist(self):
        self.assertEqual(get_friendslist(self.context), [self.faith])
        self.relationship.delete()
        self.assertEqual(get_friendslist(self.context), [])

    def test_get_default_relationship(self):
        info = get_relationship(self.context, self.faith)
        self.assertFalse(info["is_following"])
        self.assertEqual(info["follow_statement"], "Follow this user")
        self.assertEqual(info["account_statement"], "Make this user an accountability buddy")
        self.assertEqual(info["mute_statement"], "Mute this user")

    def test_get_opposite_of_default_relationship(self):
        self.relationship.toggle_following_for_current_profile(self.buffy.profile)
        self.relationship.toggle_accountability_for_current_profile(self.buffy.profile)
        self.relationship.toggle_mute_for_current_profile(self.buffy.profile)
        info = get_relationship(self.context, self.faith)
        self.assertTrue(info["is_following"])
        self.assertEqual(info["follow_statement"], "Unfollow this user")
        self.assertEqual(info["account_statement"], "Remove user as accountability buddy")
        self.assertEqual(info["mute_statement"], "Unmute this user")
