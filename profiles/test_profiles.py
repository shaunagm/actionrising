import mock
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone

from actstream.models import Action as Actstream

from actions.models import Action
from slates.models import Slate, SlateActionRelationship
from commitments.models import Commitment
from mysite.lib.choices import StatusChoices, ToDoStatusChoices, PriorityChoices, PrivacyChoices
from profiles.models import (Relationship, ProfileActionRelationship,
    ProfileSlateRelationship)
from profiles.templatetags.profile_extras import get_friendslist
from profiles.views import (toggle_relationships_helper, toggle_par_helper,
    manage_action_helper, mark_as_done_helper, manage_suggested_action_helper)
from mysite.lib.privacy import check_privacy
from profiles.lib.trackers import Trackers
from actions import factories as action_factories
from accounts import factories as account_factories
from slates import factories as slate_factories
from . import factories

###################
### Test models ###
###################


class TestProfileFactory(TestCase):
    """ The profile factory has to set attributes on the profile in an awkward
    way due to creating the profile in post_save signal. These test confirm
    that it is created correctly """

    def test_override(self):
        self.assertTrue(factories.Profile(verified=True).verified)
        self.assertFalse(factories.Profile(verified=False).verified)


class TestProfileMethods(TestCase):

    def setUp(self):
        super(TestProfileMethods, self).setUp()
        self.anon = AnonymousUser()

    def test_get_relationship(self):
        relationship = factories.Relationship()
        self.assertEqual(
            relationship,
            relationship.person_A.get_relationship(relationship.person_B))

    def test_get_relationship_given_own_profile(self):
        profile = factories.Profile()
        self.assertIsNone(profile.get_relationship(profile))

    def test_get_relationship_when_no_relationship_exists(self):
        profile1, profile2 = factories.Profile.create_batch(2)
        self.assertIsNone(profile1.get_relationship(profile2))

    def test_get_followers(self):
        relationship = factories.Relationship(B_follows_A=True)
        profile_A = relationship.person_A
        profile_B = relationship.person_B

        self.assertEqual(list(profile_A.get_followers), [profile_B])
        self.assertEqual(list(profile_B.get_followers), [])

        profile_C = factories.Profile()
        self.assertEqual(list(profile_C.get_followers), [])

    def test_get_people_user_follows(self):
        relationship = factories.Relationship(B_follows_A=True)
        profile_A = relationship.person_A
        profile_B = relationship.person_B
        self.assertEqual(list(profile_B.get_people_user_follows()), [profile_A])
        self.assertEqual(list(profile_A.get_people_user_follows()), [])

        profile_C = factories.Profile()
        self.assertEqual(list(profile_C.get_people_user_follows()), [])

    def test_get_par_given_action(self):
        par = factories.ProfileActionRelationship()
        self.assertEqual(
            par,
            par.profile.get_par_given_action(par.action))

    def test_get_open_actions(self):
        par = factories.ProfileActionRelationship()
        self.assertEqual(
            par.action,
            par.profile.get_open_actions().get())

    def test_get_suggested_actions(self):
        par = factories.ProfileActionRelationship(
            status=ToDoStatusChoices.suggested)

        self.assertEqual(
            par,
            par.profile.get_suggested_actions().get())

    def test_is_visible_follows(self):
        relationship = factories.Relationship(
            person_A__privacy=PrivacyChoices.follows,
            person_B__privacy=PrivacyChoices.follows,
            A_follows_B=True)
        self.assertTrue(relationship.person_A.is_visible_to(relationship.person_B.user))
        self.assertFalse(relationship.person_B.is_visible_to(relationship.person_A.user))

    def test_is_visible_public(self):
        profile1 = factories.Profile(privacy=PrivacyChoices.public)
        profile2 = factories.Profile()

        self.assertTrue(profile1.is_visible_to(profile2.user))
        self.assertTrue(profile1.is_visible_to(self.anon))

    def test_is_visible_sitewide(self):
        profile1 = factories.Profile(privacy=PrivacyChoices.sitewide)
        profile2 = factories.Profile()

        self.assertTrue(profile1.is_visible_to(profile2.user))
        self.assertFalse(profile1.is_visible_to(self.anon))

    def test_default_privacy(self):
        profile = factories.Profile()
        self.assertEqual(profile.current_privacy, PrivacyChoices.public)

    def test_profile_creator(self):
        profile = factories.Profile()
        self.assertEqual(profile.get_creator(), profile.user)

    def test_action_creator(self):
        action = action_factories.Action()
        self.assertEqual(action.get_creator(), action.creator)

    def test_slate_creator(self):
        slate = slate_factories.Slate()
        self.assertEqual(slate.get_creator(), slate.creator)

    def test_par_creator(self):
        # The owner of the profile in the PAR 'owns' the PAR
        par = factories.ProfileActionRelationship()
        self.assertEqual(par.get_creator(), par.profile.user)

    def test_sar_creator(self):
        # The creator of the slate 'owns' the SAR
        sar = slate_factories.SlateActionRelationship()
        self.assertEqual(sar.get_creator(), sar.slate.creator)

    def test_get_percent_finished(self):
        profile = factories.Profile()
        self.assertEqual(profile.get_percent_finished(), 0.0)

        factories.ProfileActionRelationship(profile=profile, status=ToDoStatusChoices.done)
        factories.ProfileActionRelationship.create_batch(2, profile=profile)

        self.assertEqual(profile.get_percent_finished(), 33.3)

    def test_format_suggesters(self):
        buffy = User.objects.create(username="buffysummers")
        par = factories.ProfileActionRelationship()
        self.assertEqual(par.format_suggesters([buffy]), "<a href='/profiles/profile/buffysummers/'> buffysummers </a>")

    def test_get_suggester_html(self):
        suggester = User.objects.create(username="moorecheyenne")
        par = factories.ProfileActionRelationship(last_suggester = suggester)
        self.assertEqual(par.get_suggester_html(), "<a href='/profiles/profile/moorecheyenne/'> moorecheyenne </a> suggests")


class TestStreak(TestCase):
    def setUp(self):
        super(TestStreak, self).setUp()
        self.profile = factories.Profile()

    def test_get_action_streak(self):
        self.assertEqual(self.profile.get_action_streak(), 0)
        # streak of 1: today

        today = timezone.now()
        day = timezone.timedelta(days=1)

        factories.ProfileActionRelationship(
            profile=self.profile,
            date_finished=today,
            status=ToDoStatusChoices.done
        )

        self.assertEqual(self.profile.get_action_streak(), 1)

        par = factories.ProfileActionRelationship(
            profile=self.profile,
            date_finished=today - day,
            status=ToDoStatusChoices.done
        )

        self.assertEqual(self.profile.get_action_streak(), 2)

        par.date_finished = today - 2 * day
        par.save()

        self.assertEqual(self.profile.get_action_streak(), 1)

        par.date_finished = today - day
        par.save()

        self.assertEqual(self.profile.get_action_streak(), 2)


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

    def test_current_profile_accountable_to_target_2(self):
        self.relationship.B_mutes_A = True
        self.relationship.save()
        self.assertFalse(self.relationship.current_profile_mutes_target(self.buffy.profile))
        self.assertTrue(self.relationship.current_profile_mutes_target(self.faith.profile))
        self.assertIsNone(self.relationship.current_profile_mutes_target(self.lorne.profile))

    def test_not_following_visibility(self):
        relationship = factories.Relationship(
            person_A__privacy=PrivacyChoices.follows,
            person_B__privacy=PrivacyChoices.follows)
        self.assertFalse(check_privacy(relationship.person_A, relationship.person_B.user))

    def test_toggle_following(self):
        relationship = factories.Relationship(
            person_A__privacy=PrivacyChoices.follows,
            person_B__privacy=PrivacyChoices.follows)

        # NOTE: can't also assert check privacy before since followers list is
        # cached on the instance
        self.assertTrue(relationship.toggle_following_for_current_profile(relationship.person_A))
        self.assertTrue(relationship.A_follows_B)

        self.assertTrue(check_privacy(relationship.person_A, relationship.person_B.user))

        self.assertFalse(relationship.B_follows_A)
        self.assertFalse(check_privacy(relationship.person_B, relationship.person_A.user))

    def test_toggle_following_twice(self):
        relationship = factories.Relationship(
            person_A__privacy=PrivacyChoices.follows,
            person_B__privacy=PrivacyChoices.follows)

        # NOTE: can't also assert check privacy before since followers list is
        # cached on the instance
        self.assertTrue(relationship.toggle_following_for_current_profile(relationship.person_A))
        self.assertFalse(relationship.toggle_following_for_current_profile(relationship.person_A))
        self.assertFalse(relationship.B_follows_A)
        self.assertFalse(check_privacy(relationship.person_A, relationship.person_B.user))

        # Toggling in one direction should not effect the other direction
        self.assertTrue(relationship.toggle_following_for_current_profile(relationship.person_B))

    def test_toggle_unrelated_profile(self):
        relationship = factories.Relationship()
        other_profile = factories.Profile()
        self.assertIsNone(relationship.toggle_following_for_current_profile(other_profile))

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
        self.lorne = account_factories.User()

        self.par = factories.ProfileActionRelationship()
        self.action = self.par.action
        self.buffy = self.par.profile.user
        self.slate = slate_factories.Slate()

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
        self.par = factories.ProfileActionRelationship(status=ToDoStatusChoices.suggested)

    def test_manage_suggested_action_helper_accept(self):
        self.assertEqual(self.par.status, ToDoStatusChoices.suggested)
        par = manage_suggested_action_helper(self.par, "accept")
        self.assertEqual(par.status, ToDoStatusChoices.accepted)

    def test_manage_suggested_action_helper_reject(self):
        self.assertEqual(self.par.status, ToDoStatusChoices.suggested)
        par = manage_suggested_action_helper(self.par, "decline")
        self.assertEqual(par.status, ToDoStatusChoices.rejected)

#########################
### Test templatetags ###
#########################

class TestProfileExtras(TestCase):

    def setUp(self):
        self.relationship = factories.Relationship(
            person_A__user__username="buffysummers",
            person_B__user__username="faithlehane")
        self.buffy = self.relationship.person_A.user
        self.faith = self.relationship.person_B.user

        par = factories.ProfileActionRelationship(
            action__creator=self.buffy,
            profile=self.buffy.profile)
        factories.ProfileActionRelationship(
            action=par.action,
            profile=self.faith.profile)

        class MockRequest(object):
            user = self.buffy
        self.context = {'request': MockRequest(), 'action': par.action}

    def test_get_friendslist(self):
        self.assertEqual(get_friendslist(self.context), [self.faith])
        self.relationship.delete()
        self.assertEqual(get_friendslist(self.context), [])


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
        self.assertEqual(self.profile.current_privacy, PrivacyChoices.public)

    def test_update_to_inherit_privacy(self):
        self.profile.privacy = PrivacyChoices.follows
        self.profile.save()

        self.assertEqual(self.profile.privacy, PrivacyChoices.follows)

        self.profile.privacy = PrivacyChoices.inherit
        self.profile.save()

        self.assertEqual(self.profile.privacy, PrivacyChoices.inherit)
        self.assertEqual(self.profile.current_privacy, PrivacyChoices.public)


class TestUpdatePrivacyDefaults(TestCase):

    def test_update_default(self):
        buffy = User.objects.create(username="buffysummers")
        action = buffy.action_set.create(privacy=PrivacyChoices.inherit)
        slate = buffy.slate_set.create(privacy=PrivacyChoices.inherit)

        self.assertEqual(action.current_privacy, PrivacyChoices.public)
        self.assertEqual(slate.current_privacy, PrivacyChoices.public)

        buffy.profile.privacy_defaults.global_default = PrivacyChoices.follows
        buffy.profile.privacy_defaults.save()

        action.refresh_from_db()
        self.assertEqual(action.current_privacy, PrivacyChoices.follows)

        slate.refresh_from_db()
        self.assertEqual(slate.current_privacy, PrivacyChoices.follows)

        buffy.profile.refresh_from_db()
        self.assertEqual(buffy.profile.current_privacy, PrivacyChoices.follows)


class TestEditProfiles(TestCase):
    def setUp(self):
        super(TestEditProfiles, self).setUp()
        self.buffy = User.objects.create(
            first_name="Buffy",
            last_name="Summers",
            username="buffysummers")
        self.client.force_login(self.buffy)

    def test_initial(self):
        resp = self.client.get(reverse("edit_profile"))
        self.assertEqual(resp.status_code, 200)

        form = resp.context['form']
        self.assertEqual(form.initial['first_name'], "Buffy")
        self.assertEqual(form.initial['last_name'], "Summers")
        self.assertEqual(form.initial['privacy_default'], PrivacyChoices.public)

    def test_save(self):
        resp = self.client.post(reverse("edit_profile"), {
            "first_name": "Dinnah",
            "last_name": "Saur",
            "description": "Rawr",
            "privacy": PrivacyChoices.inherit,
            "privacy_default": PrivacyChoices.follows,
        })

        self.assertEqual(resp.status_code, 302)

        saved_buffy = User.objects.get(pk=self.buffy.pk)
        self.assertEqual(saved_buffy.first_name, "Dinnah")
        self.assertEqual(saved_buffy.last_name, "Saur")
        self.assertEqual(saved_buffy.profile.description, "Rawr")
        self.assertEqual(saved_buffy.profile.privacy_defaults.global_default,
                         PrivacyChoices.follows)


@mock.patch("profiles.managers.apply_check_privacy", autospec=True)
class TestOthersActionFeed(TestCase):
    """ make sure that the feed of others' actions on Actions is accurate """

    def setUp(self):
        self.action = action_factories.Action()
        self.assertTrue(self.action.target_actions.exists())

    def test_exclude_my_action(self, apply_check_privacy):
        user = self.action.creator
        apply_check_privacy.return_value = []

        stream = Actstream.objects.others(user)
        self.assertEqual(
            apply_check_privacy.call_args_list,
            [mock.call([], user, True),  # actions
             mock.call([], user, True),  # slates
             mock.call([], user, True)  # users
             ])

        self.assertFalse(stream)

    def test_show_others_public_action(self, apply_check_privacy):
        profile = factories.Profile()
        user = profile.user
        apply_check_privacy.side_effect = [[self.action], [], [self.action.creator]]

        stream = Actstream.objects.others(user)
        self.assertEqual(
            apply_check_privacy.call_args_list,
            [mock.call([self.action], user, True),  # actions
             mock.call([], user, True),  # slates
             mock.call([self.action.creator], user, True)  # users
             ])

        self.assertTrue(stream)

    def test_hide_private_actions(self, apply_check_privacy):
        profile = factories.Profile()
        user = profile.user
        apply_check_privacy.return_value = []

        stream = Actstream.objects.others(user)
        self.assertEqual(
            apply_check_privacy.call_args_list,
            [mock.call([self.action], user, True),  # actions
             mock.call([], user, True),  # slates
             mock.call([self.action.creator], user, True)  # users
             ])

        self.assertFalse(stream)


@mock.patch("profiles.managers.apply_check_privacy", autospec=True)
class TestOthersSlateFeed(TestCase):
    """ make sure that the feed of others' actions on Slates is accurate """

    def setUp(self):
        self.slate = slate_factories.Slate()
        self.assertTrue(self.slate.target_actions.exists())

    def test_exclude_my_slate(self, apply_check_privacy):
        user = self.slate.creator
        apply_check_privacy.return_value = []

        stream = Actstream.objects.others(user)
        self.assertEqual(
            apply_check_privacy.call_args_list,
            [mock.call([], user, True),  # actions
             mock.call([], user, True),  # slates
             mock.call([], user, True)  # users
             ])

        self.assertFalse(stream)

    def test_show_others_public_slate(self, apply_check_privacy):
        profile = factories.Profile()
        user = profile.user
        apply_check_privacy.side_effect = [[], [self.slate], [self.slate.creator]]

        stream = Actstream.objects.others(user)
        self.assertEqual(
            apply_check_privacy.call_args_list,
            [mock.call([], user, True),  # actions
             mock.call([self.slate], user, True),  # slates
             mock.call([self.slate.creator], user, True)  # users
             ])

        self.assertTrue(stream)

    def test_hide_private_slate(self, apply_check_privacy):
        profile = factories.Profile()
        user = profile.user
        apply_check_privacy.return_value = []

        stream = Actstream.objects.others(user)
        self.assertEqual(
            apply_check_privacy.call_args_list,
            [mock.call([], user, True),  # actions
             mock.call([self.slate], user, True),  # slates
             mock.call([self.slate.creator], user, True)  # users
             ])

        self.assertFalse(stream)


class ProfileOthersFeed(TestCase):
    def make_data(self):
        actstream_count = Actstream.objects.count()

        # mine
        action_factories.Action.create_batch(5, creator=self.profile.user)
        slate_factories.Slate.create_batch(5, creator=self.profile.user)
        self.assertEqual(Actstream.objects.count(), actstream_count + 10)

        # already following
        factories.ProfileSlateRelationship.create_batch(5, profile=self.profile)
        factories.ProfileActionRelationship.create_batch(5, profile=self.profile)
        self.assertEqual(Actstream.objects.count(), actstream_count + 25)

        # public
        action_factories.Action.create_batch(5)
        slate_factories.Slate.create_batch(5)
        self.assertEqual(Actstream.objects.count(), actstream_count + 35)

        # private
        action_factories.Action.create_batch(5, privacy=PrivacyChoices.follows)
        slate_factories.Slate.create_batch(5, privacy=PrivacyChoices.follows)
        self.assertEqual(Actstream.objects.count(), actstream_count + 45)

        # private but visible
        action_factories.VisibleUnfollowedAction.create_batch(5)
        slate_factories.VisibleUnfollowedSlate.create_batch(5)
        self.assertEqual(Actstream.objects.count(), actstream_count + 55)

    def test_profile(self):
        self.profile = factories.Profile()
        user = self.profile.user

        self.make_data()

        with CaptureQueriesContext(connection) as original_queries:
            self.assertEqual(Actstream.objects.others(user).count(), 20)

        self.make_data()

        with CaptureQueriesContext(connection) as final_queries:
            self.assertEqual(Actstream.objects.others(user).count(), 40)

        # something other than ContentType is being cached but the number goes down
        self.assertTrue(len(final_queries) < len(original_queries))
