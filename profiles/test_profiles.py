from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User, AnonymousUser
from actions.models import Action
from slates.models import Slate, SlateActionRelationship
from commitments.models import Commitment
from mysite.lib.choices import StatusChoices, ToDoStatusChoices, PriorityChoices, PrivacyChoices
from profiles.models import (Profile, Relationship, ProfileActionRelationship,
    ProfileSlateRelationship)
from profiles.templatetags.profile_extras import get_friendslist
from profiles.views import (toggle_relationships_helper, toggle_par_helper,
    manage_action_helper, mark_as_done_helper, manage_suggested_action_helper)
from profiles.lib import status_helpers
from profiles.lib.trackers import Trackers
from mysite.lib.privacy import check_privacy

###################
### Test models ###
###################

class TestProfileMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.buffy.profile.current_privacy = 'follows'
        self.buffy.save()
        self.faith = User.objects.create(username="faithlehane")
        self.faith.profile.current_privacy = 'follows'
        self.faith.save()
        self.relationship = Relationship.objects.create(person_A=self.buffy.profile,
            person_B=self.faith.profile)
        self.relationship.B_follows_A = True
        self.relationship.save()
        self.lorne = User.objects.create(username="lorne") # Relationshipless
        self.willow = User.objects.create(username="willow")
        self.willow.profile.current_privacy = 'sitewide'
        self.willow.save()
        self.action = Action.objects.create(slug="test-action", title="Test Action", creator=self.buffy)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)
        self.slate = Slate.objects.create(slug="test-slate", title="Test Slate", creator=self.faith)
        self.sar = SlateActionRelationship.objects.create(slate=self.slate, action=self.action)
        self.anon = AnonymousUser()

    def test_get_relationship(self):
        relationship = self.buffy.profile.get_relationship(self.faith.profile)
        self.assertEqual(relationship, self.relationship)

    def test_get_relationship_given_own_profile(self):
        relationship = self.buffy.profile.get_relationship(self.buffy.profile)
        self.assertIsNone(relationship)

    def test_get_relationship_when_no_relationship_exists(self):
        relationship = self.buffy.profile.get_relationship(self.lorne.profile)
        self.assertIsNone(relationship)

    def test_get_followers(self):
        self.assertEqual(list(self.buffy.profile.get_followers()), [self.faith.profile])
        self.assertEqual(list(self.faith.profile.get_followers()), [])
        self.assertEqual(list(self.lorne.profile.get_followers()), [])

    def test_get_people_user_follows(self):
        self.assertEqual(list(self.buffy.profile.get_people_user_follows()), [])
        self.assertEqual(list(self.lorne.profile.get_people_user_follows()), [])
        self.assertEqual(list(self.faith.profile.get_people_user_follows()), [self.buffy.profile])

    def test_get_par_given_action(self):
        par = self.buffy.profile.get_par_given_action(self.action)
        self.assertEqual(par.profile, self.buffy.profile)
        self.assertEqual(par.action, self.action)
        self.assertEqual(par.pk, self.par.pk)

    def test_get_open_actions(self):
        self.assertEqual(self.buffy.profile.get_open_actions(), [self.action])

    def test_get_suggested_actions(self):
        self.par.status = ToDoStatusChoices.suggested
        self.par.save()
        self.assertEqual(list(self.buffy.profile.get_suggested_actions()), [self.par])
        self.assertEqual(self.buffy.profile.get_suggested_actions_count(), 1)

    def test_is_visible(self):
        self.assertTrue(self.faith.profile.is_visible_to(self.buffy))
        self.assertFalse(self.buffy.profile.is_visible_to(self.faith))
        self.assertTrue(self.lorne.profile.is_visible_to(self.buffy))
        self.assertTrue(self.lorne.profile.is_visible_to(self.anon))
        self.assertTrue(self.willow.profile.is_visible_to(self.buffy))
        self.assertFalse(self.willow.profile.is_visible_to(self.anon))

    def test_default_privacy(self):
        self.assertEqual(self.lorne.profile.current_privacy, 'public')

    def test_profile_creator(self):
        self.assertFalse(self.faith.profile.get_creator() == self.buffy)
        self.assertTrue(self.faith.profile.get_creator() == self.faith)
        self.assertFalse(self.faith.profile.get_creator() == self.anon)

    def test_action_creator(self):
        self.assertFalse(self.action.get_creator() == self.faith)
        self.assertTrue(self.action.get_creator() == self.buffy)
        self.assertFalse(self.action.get_creator() == self.anon)

    def test_slate_creator(self):
        self.assertFalse(self.slate.get_creator() == self.buffy)
        self.assertTrue(self.slate.get_creator() == self.faith)
        self.assertFalse(self.slate.get_creator() == self.anon)

    def test_par_creator(self):
        # The owner of the profile in the PAR 'owns' the PAR
        self.assertFalse(self.par.get_creator() == self.faith)
        self.assertTrue(self.par.get_creator() == self.buffy)
        self.assertFalse(self.par.get_creator() == self.anon)

    def test_sar_creator(self):
        # The creator of the slate 'owns' the SAR
        self.assertFalse(self.sar.get_creator() == self.buffy)
        self.assertTrue(self.sar.get_creator() == self.faith)
        self.assertFalse(self.sar.get_creator() == self.anon)

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
        self.buffy.profile.current_privacy = PrivacyChoices.follows
        self.buffy.profile.save()
        self.faith.profile.current_privacy = PrivacyChoices.follows
        self.faith.profile.save()
        # Starting with A (Buffy) not following B (Faith)
        self.assertFalse(self.relationship.A_follows_B)
        self.assertFalse(check_privacy(self.buffy.profile, self.faith))
        # Toggle returns the new status, which is True - Buffy does now follow Faith
        self.assertTrue(self.relationship.toggle_following_for_current_profile(self.buffy.profile))
        # Confirm A now follows B
        self.assertTrue(self.relationship.A_follows_B)
        self.assertTrue(check_privacy(self.buffy.profile, self.faith))
        # Confirm B does not follow A
        self.assertFalse(self.relationship.B_follows_A)
        self.assertFalse(check_privacy(self.faith.profile, self.buffy))
        # Toggle back to not following
        self.assertFalse(self.relationship.toggle_following_for_current_profile(self.buffy.profile))
        self.assertFalse(check_privacy(self.buffy.profile, self.faith))
        # Toggle the other direction - B (Faith) following A (Buffy)
        self.assertTrue(self.relationship.toggle_following_for_current_profile(self.faith.profile))
        self.assertTrue(check_privacy(self.faith.profile, self.buffy))
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

    def test_get_people_user_follows(self):
        self.relationship.toggle_following_for_current_profile(self.buffy.profile)
        self.assertEquals(list(self.buffy.profile.get_people_user_follows()), [self.faith.profile])

class TestParMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(slug="test-action", title="Test Action", creator=self.buffy)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)

    def test_add_suggester(self):
        self.assertEqual(self.par.get_suggesters(), [])
        self.par.add_suggester(self.faith.username)
        self.assertEqual(self.par.get_suggesters(), ['faithlehane'])

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
        self.assertEqual(par.status, ToDoStatusChoices.accepted)

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
        self.slate = Slate.objects.create(slug="test-slate", creator=self.faith, title="Test Slate")
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)
        class MockForm(object):
            cleaned_data = {'priority': PriorityChoices.high, 'status': ToDoStatusChoices.done, 'privacy': PrivacyChoices.public,
                'profiles': [self.lorne.profile], 'slates': [self.slate], 'notes': "A note"}
        self.mock_form = MockForm()

    def test_changes_fields_from_defaults(self):
        self.assertEqual([self.par.priority, self.par.status], [PriorityChoices.medium, ToDoStatusChoices.accepted])
        manage_action_helper(self.par, self.mock_form, self.buffy)
        self.assertEqual([self.par.priority, self.par.status], [PriorityChoices.high, ToDoStatusChoices.done])

    def test_make_new_par_for_profile(self):
        with self.assertRaises(ObjectDoesNotExist):
            ProfileActionRelationship.objects.get(profile=self.lorne.profile, action=self.action)
        manage_action_helper(self.par, self.mock_form, self.buffy)
        par = ProfileActionRelationship.objects.get(profile=self.lorne.profile, action=self.action)
        self.assertEqual(par.profile.user, self.lorne)

    def test_make_new_sar_for_action(self):
        with self.assertRaises(ObjectDoesNotExist):
            SlateActionRelationship.objects.get(slate=self.slate, action=self.action)
        manage_action_helper(self.par, self.mock_form, self.buffy)
        sar = SlateActionRelationship.objects.get(slate=self.slate, action=self.action)
        self.assertEqual(sar.slate, self.slate)

class TestMarkAsDoneView(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(slug="test-action", creator=self.buffy)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)

    def test_mark_as_accepted(self):
        self.assertEqual(self.par.status, ToDoStatusChoices.accepted)
        par = mark_as_done_helper(self.buffy.profile, self.action, "done")
        self.assertEqual(par.status, ToDoStatusChoices.done)
        par = mark_as_done_helper(self.buffy.profile, self.action, "accepted")
        self.assertEqual(par.status, ToDoStatusChoices.accepted)

class TestManageSuggestedActionView(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(slug="test-action", creator=self.buffy)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile,
            action=self.action, last_suggester=self.faith, status=ToDoStatusChoices.suggested)

    def test_manage_suggested_action_helper_accept(self):
        self.assertEqual(self.par.status, ToDoStatusChoices.suggested)
        par = manage_suggested_action_helper(self.par, "accept")
        self.assertEqual(par.status, ToDoStatusChoices.accepted)

    def test_manage_suggested_action_helper_reject(self):
        self.assertEqual(self.par.status, ToDoStatusChoices.suggested)
        par = manage_suggested_action_helper(self.par, "reject")
        self.assertEqual(par.status, ToDoStatusChoices.rejected)

#########################
### Test templatetags ###
#########################

class TestProfileExtras(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.relationship = Relationship.objects.create(person_A=self.buffy.profile,
            person_B=self.faith.profile)
        self.action = Action.objects.create(slug="test-action", title="Test Action", creator=self.buffy)
        self.par = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)
        self.faith_par = ProfileActionRelationship.objects.create(profile=self.faith.profile, action=self.action)
        class MockRequest(object):
            user = self.buffy
        self.context = {'request': MockRequest(), 'action': self.action}

    def test_get_friendslist(self):
        self.assertEqual(get_friendslist(self.context), [self.faith])
        self.relationship.delete()
        self.assertEqual(get_friendslist(self.context), [])

    def get_status_phrase(self):
        assertEqual(get_status_phrase('suggested'), 'Suggested to')

    #TODO test filtered feed
    def test_filtered_feed(self):
        pass

################
### Test lib ###
################

class TestStatusHelper(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(slug="test-action", title="Test Action", creator=self.faith)
        ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)
        Commitment.objects.create(profile=self.buffy.profile, action=self.action)

    def test_close_accepted_pars_when_action_closes(self):
        self.action.status = StatusChoices.finished
        self.action.save()
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(par.status, ToDoStatusChoices.closed)

    def test_delete_suggested_pars_when_action_closes(self):
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)
        par.status = ToDoStatusChoices.suggested
        par.save()
        self.action.status = StatusChoices.withdrawn
        self.action.save()
        par = ProfileActionRelationship.objects.filter(profile=self.buffy.profile, action=self.action)
        self.assertFalse(par)

    def test_open_pars_when_action_reopens(self):
        # Close action
        self.action.status = StatusChoices.finished
        self.action.save()
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(par.status, ToDoStatusChoices.closed)
        # Reopen action
        self.action.status = StatusChoices.ready
        self.action.save()
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(par.status, ToDoStatusChoices.accepted)

    def test_close_commitment_when_PAR_is_closed(self):
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)
        par.status = ToDoStatusChoices.closed
        par.save()
        com = Commitment.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(com.status, "removed")

    def test_open_commitment_when_PAR_is_reopened(self):
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=self.action)
        par.status = ToDoStatusChoices.closed
        par.save()
        com = Commitment.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(com.status, "removed")
        par.status = ToDoStatusChoices.accepted
        par.save()
        com = Commitment.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(com.status, "active")

    def test_close_commitment_when_action_is_closed(self):
        '''Ties the helpers together'''
        # Close action
        self.action.status = StatusChoices.finished
        self.action.save()
        com = Commitment.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(com.status, "removed")

    def test_reopen_commitment_when_action_is_reopened(self):
        '''Ties the helpers together'''
        # Close action
        self.action.status = StatusChoices.finished
        self.action.save()
        # Reopen action
        self.action.status = StatusChoices.ready
        self.action.save()
        # Test
        com = Commitment.objects.get(profile=self.buffy.profile, action=self.action)
        self.assertEqual(com.status, "active")

class TestTrackers(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.faith = User.objects.create(username="faithlehane")
        self.vampire = User.objects.create(username="vampire")
        self.vampire.profile.privacy = PrivacyChoices.follows
        self.vampire.profile.save()

        self.action = Action.objects.create(slug="test-action", title="Test Action", creator=self.faith)
        self.slate = Slate.objects.create(slug="test-slate", creator=self.faith, title="Test Slate")

        # buffy tracks action
        ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)
        # slate tracks action
        SlateActionRelationship.objects.create(slate=self.slate, action=self.action)
        # faith tracks slate
        ProfileSlateRelationship.objects.create(profile=self.faith.profile, slate=self.slate)

        self.action0 = Action.objects.create(slug="test-action0", title="Test Action 0", creator=self.faith)
        self.slate0 = Slate.objects.create(slug="test-slate0", creator=self.faith, title="Test Slate 0")
        self.private_slate = Slate.objects.create(slug="private-slate", creator=self.vampire, title="Private Slate")
        self.private_slate.privacy = PrivacyChoices.follows
        self.private_slate.save()

        self.action2 = Action.objects.create(slug="test-action2", title="Test Action 2", creator=self.faith)
        self.buffy_action2 = ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action2)
        self.buffy_action2.status = ToDoStatusChoices.suggested
        self.buffy_action2.save()
        self.vampire_action2 = ProfileActionRelationship.objects.create(profile=self.vampire.profile, action=self.action2, status=ToDoStatusChoices.accepted)
        self.slate_action2 = SlateActionRelationship.objects.create(slate=self.slate, action=self.action2)
        self.private_slate_action2 = SlateActionRelationship.objects.create(slate=self.private_slate, action=self.action2)

        self.slate2 = Slate.objects.create(slug="test-slate2", creator=self.faith, title="Test Slate 2")
        self.faith_slate2 = ProfileSlateRelationship.objects.create(profile=self.faith.profile, slate=self.slate2)
        self.vampire_slate2 = ProfileSlateRelationship.objects.create(profile=self.vampire.profile, slate=self.slate2)

    def test_has_people(self):
        self.assertTrue(Trackers(self.action, self.buffy).has_people)
        self.assertTrue(Trackers(self.slate, self.buffy).has_people)
        self.assertFalse(Trackers(self.action0, self.buffy).has_people)
        self.assertFalse(Trackers(self.slate0, self.buffy).has_people)

    def test_has_slates(self):
        self.assertTrue(Trackers(self.action, self.buffy).has_slates)
        self.assertFalse(Trackers(self.action0, self.buffy).has_slates)

    def test_people_phrase(self):
        self.assertEqual(Trackers(self.action, self.buffy).people_phrase, '1 person')
        self.assertEqual(Trackers(self.action0, self.buffy).people_phrase, '0 people')
        self.assertEqual(Trackers(self.action2, self.buffy).people_phrase, '2 people')
        self.assertEqual(Trackers(self.slate, self.buffy).people_phrase, '1 person')
        self.assertEqual(Trackers(self.slate0, self.buffy).people_phrase, '0 people')
        self.assertEqual(Trackers(self.slate2, self.buffy).people_phrase, '2 people')

    def test_slate_phrase(self):
        self.assertEqual(Trackers(self.action, self.buffy).slate_phrase, '1 slate')
        self.assertEqual(Trackers(self.action0, self.buffy).slate_phrase, '0 slates')
        self.assertEqual(Trackers(self.action2, self.buffy).slate_phrase, '2 slates')

    def test_people_tracking_by_status(self):
        data_iterator = Trackers(self.action2, self.buffy).people_tracking_by_status
        data = dict(data_iterator())
        self.assertEqual(len(data.keys()), 2)
        self.assertEqual(data['suggested']['total_count'], 1)
        self.assertEqual(data['suggested']['restricted_count'], 0)
        self.assertEqual(data['suggested']['visible_list'], [self.buffy_action2])
        self.assertEqual(data['accepted']['total_count'], 1)
        self.assertEqual(data['accepted']['restricted_count'], 1)
        self.assertEqual(data['accepted']['visible_list'], [])

    def test_slates_tracking_by_privacy(self):
        data = Trackers(self.action2, self.buffy).slates_tracking_by_privacy
        self.assertEqual(data['total_count'], 2)
        # buffy can't see vampire's slate
        self.assertEqual(data['restricted_count'], 1)
        # buffy can see faith's slate
        self.assertEqual(data['visible_list'], [self.slate_action2])

    def test_people_tracking_by_privacy(self):
        data = Trackers(self.slate2, self.buffy).people_tracking_by_privacy
        self.assertEqual(data['total_count'], 2)
        # buffy can't see vampire
        self.assertEqual(data['restricted_count'], 1)
        # buffy can see faith
        self.assertEqual(data['visible_list'], [self.faith_slate2])


class TestProfilePrivacy(TestCase):
    def setUp(self):
        super(TestProfilePrivacy, self).setUp()
        self.buffy = User.objects.create(username="buffysummers")
        self.profile = self.buffy.profile

    def test_default(self):
        # default to the PrivacyDefaults default
        self.assertEqual(self.profile.privacy, PrivacyChoices.inherit)
        self.assertEqual(self.profile.current_privacy, PrivacyChoices.public)

    def test_concrete_privacy(self):
        self.profile.privacy = PrivacyChoices.follows
        self.profile.save()

        self.assertEqual(self.profile.privacy, PrivacyChoices.follows)
        self.assertEqual(self.profile.current_privacy, PrivacyChoices.follows)

    def test_inherit_privacy(self):
        self.profile.privacy = PrivacyChoices.inherit
        self.profile.save()

        self.assertEqual(self.profile.privacy, PrivacyChoices.inherit)
        self.assertEqual(self.profile.current_privacy, self.profile.privacy_defaults.global_default)

    def test_update_to_inherit_privacy(self):
        self.profile.privacy = PrivacyChoices.follows
        self.profile.save()

        self.assertEqual(self.profile.privacy, PrivacyChoices.follows)

        self.profile.privacy = PrivacyChoices.inherit
        self.profile.save()

        self.assertEqual(self.profile.privacy, PrivacyChoices.inherit)
        self.assertEqual(self.profile.current_privacy, self.profile.privacy_defaults.global_default)
