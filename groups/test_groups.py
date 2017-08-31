import json

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.forms.widgets import HiddenInput

from groups.models import GroupProfile, PendingMember
from mysite.lib.choices import PrivacyChoices
from groups.forms import GroupForm
from groups.lib.utils import get_potential_invitees
from groups.templatetags.groups_extras import get_user_role
from groups import views

from groups import factories as group_factories
from profiles import factories as profile_factories

###################
### Test models ###
###################

class TestGroupProfileMethods(TestCase):

    def setUp(self):
        self.groupprofile = group_factories.GroupProfile()
        self.test_member = profile_factories.Profile()
        self.test_admin = profile_factories.Profile()
        self.test_nonmember = profile_factories.Profile()
        self.test_anon_user = AnonymousUser()

    def test_hasmember(self):
        self.assertFalse(self.groupprofile.hasMember(self.test_member.user))
        self.groupprofile.group.user_set.add(self.test_member.user)
        self.assertTrue(self.groupprofile.hasMember(self.test_member.user))

    def test_addmember(self):
        self.assertFalse(self.groupprofile.hasMember(self.test_member.user))
        self.groupprofile.addMember(self.test_member.user)
        self.assertTrue(self.groupprofile.hasMember(self.test_member.user))

    def test_addmember_works_when_member_already_exists(self):
        self.assertFalse(self.groupprofile.hasMember(self.test_member.user))
        self.groupprofile.addMember(self.test_member.user)
        self.groupprofile.addMember(self.test_member.user)
        self.assertTrue(self.groupprofile.hasMember(self.test_member.user))

    def test_remove_member(self):
        self.groupprofile.addMember(self.test_member.user)
        self.assertTrue(self.groupprofile.hasMember(self.test_member.user))
        self.groupprofile.removeMember(self.test_member.user)
        self.assertFalse(self.groupprofile.hasMember(self.test_member.user))

    def test_remove_member_removes_admin(self):
        self.groupprofile.addAdmin(self.test_admin.user)
        self.assertTrue(self.groupprofile.hasMember(self.test_admin.user))
        self.groupprofile.removeMember(self.test_admin.user)
        self.assertFalse(self.groupprofile.hasMember(self.test_admin.user))

    def test_addadmin(self):
        self.assertFalse(self.groupprofile.hasAdmin(self.test_admin.user))
        self.groupprofile.addAdmin(self.test_admin.user)
        self.assertTrue(self.groupprofile.hasAdmin(self.test_admin.user))

    def test_addadmin_works_for_existing_member(self):
        self.assertFalse(self.groupprofile.hasAdmin(self.test_admin.user))
        self.groupprofile.addMember(self.test_admin.user)
        self.groupprofile.addAdmin(self.test_admin.user)
        self.assertTrue(self.groupprofile.hasAdmin(self.test_admin.user))

    def test_removeadmin(self):
        self.groupprofile.addAdmin(self.test_admin.user)
        self.assertTrue(self.groupprofile.hasAdmin(self.test_admin.user))
        self.groupprofile.removeAdmin(self.test_admin.user)
        self.assertFalse(self.groupprofile.hasAdmin(self.test_admin.user))
        # User should still be member, just not admin
        self.assertTrue(self.groupprofile.hasMember(self.test_admin.user))

    def test_create_group_on_save(self):
        '''Check that automatic group creation & the groupname helper work'''
        test_group = GroupProfile.objects.create(groupname="A test groupname",
            owner=self.test_member.user)
        self.assertEqual(test_group.group.name, "a-test-groupname")

    def test_add_owner_as_admin_on_save(self):
        test_group = GroupProfile.objects.create(groupname="A test groupname",
                                                 owner=self.test_member.user)
        self.assertTrue(test_group.hasAdmin(self.test_member.user))

    def test_get_urls(self):
        test_group = GroupProfile.objects.create(groupname="A test groupname",
                                                 owner=self.test_member.user)
        self.assertEqual(test_group.get_absolute_url(), "/groups/group/a-test-groupname/")
        self.assertEqual(test_group.get_edit_url(), "/groups/edit/a-test-groupname/")
        self.assertEqual(test_group.get_admin_url(), "/groups/admin/a-test-groupname/")

    def test_is_visible_when_public(self):
        '''Should appear to all users: member, non-member and non-user'''
        self.groupprofile.privacy = PrivacyChoices.public
        self.groupprofile.save()
        self.assertTrue(self.groupprofile.is_visible_to(self.test_anon_user))
        self.assertTrue(self.groupprofile.is_visible_to(self.test_nonmember.user))
        self.groupprofile.addMember(self.test_member.user)
        self.assertTrue(self.groupprofile.is_visible_to(self.test_member.user))

    def test_is_visible_when_sitewide(self):
        '''Should appear only to member and non-member, not non-user'''
        self.groupprofile.privacy = PrivacyChoices.sitewide
        self.groupprofile.save()
        self.assertFalse(self.groupprofile.is_visible_to(self.test_anon_user))
        self.assertTrue(self.groupprofile.is_visible_to(self.test_nonmember.user))
        self.groupprofile.addMember(self.test_member.user)
        self.assertTrue(self.groupprofile.is_visible_to(self.test_member.user))

    def test_is_visible_when_members_only(self):
        '''Should appear only to member'''
        self.groupprofile.privacy = PrivacyChoices.members
        self.groupprofile.save()
        self.assertFalse(self.groupprofile.is_visible_to(self.test_anon_user))
        self.assertFalse(self.groupprofile.is_visible_to(self.test_nonmember.user))
        self.groupprofile.addMember(self.test_member.user)
        self.assertTrue(self.groupprofile.is_visible_to(self.test_member.user))

    def test_get_members(self):
        self.groupprofile.addMember(self.test_member.user)
        self.assertEquals(list(self.groupprofile.get_members()),
            [self.groupprofile.owner, self.test_member.user])


class TestGroupForms(TestCase):

    def setUp(self):
        self.test_owner = profile_factories.Profile()
        self.groupprofile = group_factories.GroupProfile()

    def test_user_set_on_init(self):
        initial_form = GroupForm(user=self.test_owner)
        self.assertEquals(initial_form.user, self.test_owner)

    def test_groupname_hidden_on_update(self):
        update_form = GroupForm(instance=self.groupprofile)
        self.assertEqual(type(update_form.fields['groupname'].widget), HiddenInput)

###################
### Test utils  ###
###################

class TestGroupUtils(TestCase):

    def setUp(self):
        self.test_inviter = profile_factories.Profile()
        self.groupprofile = group_factories.GroupProfile(owner=self.test_inviter.user)

    def test_unconnected_profiles_ineligible_invitees(self):
        unconnected_profile = profile_factories.Profile()
        filtered = get_potential_invitees(self.groupprofile, self.test_inviter.user)
        self.assertEqual(filtered, [])

    def test_connections_who_dont_follow_you_are_ineligible_invitees(self):
        nonfollower_profile = profile_factories.Profile()
        rel = profile_factories.Relationship(person_A=self.test_inviter,
            person_B= nonfollower_profile)
        rel.toggle_following_for_current_profile(self.test_inviter)
        filtered = get_potential_invitees(self.groupprofile,
            self.test_inviter.user)
        self.assertEqual(filtered, [])

    def test_connections_who_do_follow_you_are_eligible_invitees(self):
        follower_profile = profile_factories.Profile()
        rel = profile_factories.Relationship(person_A=self.test_inviter,
                                             person_B=follower_profile)
        rel.toggle_following_for_current_profile(follower_profile)
        filtered = get_potential_invitees(self.groupprofile,
                                          self.test_inviter.user)
        self.assertEqual(filtered, [follower_profile])

    def test_members_are_ineligible_invitees(self):
        follower_profile = profile_factories.Profile()
        rel = profile_factories.Relationship(person_A=self.test_inviter,
                                             person_B=follower_profile)
        rel.toggle_following_for_current_profile(follower_profile)
        filtered = get_potential_invitees(self.groupprofile,
                                          self.test_inviter.user)
        self.assertEqual(filtered, [follower_profile])
        self.groupprofile.addMember(follower_profile.user)
        filtered = get_potential_invitees(self.groupprofile,
                                          self.test_inviter.user)
        self.assertEqual(filtered, [])

    def test_pending_members_are_ineligible_invitees(self):
        follower_profile = profile_factories.Profile()
        rel = profile_factories.Relationship(person_A=self.test_inviter,
                                             person_B=follower_profile)
        rel.toggle_following_for_current_profile(follower_profile)
        filtered = get_potential_invitees(self.groupprofile,
                                          self.test_inviter.user)
        self.assertEqual(filtered, [follower_profile])
        PendingMember.objects.create(group=self.groupprofile, user=follower_profile.user)
        filtered = get_potential_invitees(self.groupprofile,
                                          self.test_inviter.user)
        self.assertEqual(filtered, [])


##################
### Test tags  ###
##################

class TestGroupTemplateTags(TestCase):

    def setUp(self):

        self.test_inviter = profile_factories.Profile()
        self.groupprofile = group_factories.GroupProfile(owner=self.test_inviter.user)
        self.context = {'object': self.groupprofile }

    def test_get_user_role(self):
        self.assertEqual(get_user_role(self.context, self.test_inviter.user), "owner")
        admin = profile_factories.Profile()
        self.groupprofile.addAdmin(admin.user)
        self.assertEqual(get_user_role(self.context, admin.user), "admin")
        member = profile_factories.Profile()
        self.groupprofile.addMember(member.user)
        self.assertEqual(get_user_role(self.context, member.user), "member")
        nonmember = profile_factories.Profile()
        self.assertIsNone(get_user_role(self.context, nonmember.user))


#######################
### Test AJAX views ###
#######################

class TestGroupAJAXViews(TestCase):

    def setUp(self):
        self.test_owner = profile_factories.Profile().user
        self.groupprofile = group_factories.GroupProfile(owner=self.test_owner)
        self.test_admin = profile_factories.Profile().user
        self.groupprofile.addAdmin(self.test_admin)
        self.test_member = profile_factories.Profile().user
        self.groupprofile.addMember(self.test_member)
        self.factory = RequestFactory()

    def test_join_group_works_if_membership_is_open(self):
        test_user = profile_factories.Profile().user
        request = self.factory.get('/join_group', {'group_pk': str(self.groupprofile.pk)})
        request.user = test_user
        response = views.join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You have joined this group.")
        self.assertTrue(self.groupprofile.hasMember(test_user))

    def test_join_group_fails_if_already_in_group(self):
        request = self.factory.get('/join_group', {'group_pk': str(self.groupprofile.pk)})
        request.user = self.test_member
        response = views.join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You are already a member of this group.")
        self.assertTrue(self.groupprofile.hasMember(self.test_member))

    def test_join_group_fails_if_membership_is_closed(self):
        self.groupprofile.membership = "request"
        self.groupprofile.save()
        test_user = profile_factories.Profile().user
        request = self.factory.get('/join_group', {'group_pk': str(self.groupprofile.pk)})
        request.user = test_user
        response = views.join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "There was an error joining this group.")
        self.assertFalse(self.groupprofile.hasMember(test_user))

    def test_leave_group_fails_if_owner(self):
        request = self.factory.get('/leave_group', {'group_pk': str(self.groupprofile.pk)})
        request.user = self.test_owner
        response = views.leave_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You cannot leave this group because you are the owner.")
        self.assertTrue(self.groupprofile.hasMember(self.test_owner))

    def test_leave_group_succeeds_if_not_owner(self):
        request = self.factory.get('/leave_group', {'group_pk': str(self.groupprofile.pk)})
        request.user = self.test_member
        response = views.leave_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You have left this group.")
        self.assertFalse(self.groupprofile.hasMember(self.test_member))

    def test_remove_from_group_fails_if_selfremoval(self):
        request = self.factory.get('/remove_from_group',
            {'group_pk': str(self.groupprofile.pk), 'user_pk': str(self.test_member.pk)})
        request.user = self.test_member
        response = views.remove_from_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You cannot remove yourself from the group.")
        self.assertTrue(self.groupprofile.hasMember(self.test_member))

    def test_remove_from_group_lets_admin_remove_member(self):
        request = self.factory.get('/remove_from_group',
            {'group_pk': str(self.groupprofile.pk), 'user_pk': str(self.test_member.pk)})
        request.user = self.test_admin
        response = views.remove_from_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "User has been removed from group.")
        self.assertFalse(self.groupprofile.hasMember(self.test_member))

    def test_remove_from_group_prevents_admin_from_removing_admin(self):
        self.groupprofile.addAdmin(self.test_member)
        request = self.factory.get('/remove_from_group',
            {'group_pk': str(self.groupprofile.pk), 'user_pk': str(self.test_member.pk)})
        request.user = self.test_admin
        response = views.remove_from_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You do not have permission to remove admins.")
        self.assertTrue(self.groupprofile.hasMember(self.test_member))

    def test_remove_from_group_lets_owner_remove_admin(self):
        request = self.factory.get('/remove_from_group',
            {'group_pk': str(self.groupprofile.pk), 'user_pk': str(self.test_admin.pk)})
        request.user = self.test_owner
        response = views.remove_from_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "User has been removed from group.")
        self.assertFalse(self.groupprofile.hasMember(self.test_admin))

    def test_request_to_join_group_succeeds_if_membership_set_to_request(self):
        self.groupprofile.membership = "request"
        self.groupprofile.save()
        test_user = profile_factories.Profile().user
        request = self.factory.get('/request_to_join_group',
            {'group_pk': str(self.groupprofile.pk)})
        request.user = test_user
        response = views.request_to_join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You have requested to join this group.")
        pending = PendingMember.objects.filter(user=test_user, group=self.groupprofile)
        self.assertEquals(len(pending), 1)

    def test_request_to_join_group_fails_if_membership_set_to_open(self):
        test_user = profile_factories.Profile().user
        request = self.factory.get('/request_to_join_group',
            {'group_pk': str(self.groupprofile.pk)})
        request.user = test_user
        response = views.request_to_join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "There was an error processing your request to join this group.")
        pending = PendingMember.objects.filter(user=test_user, group=self.groupprofile)
        self.assertEquals(len(pending), 0)

    def test_request_to_join_group_fails_if_membership_set_to_invite(self):
        self.groupprofile.membership = "invite"
        self.groupprofile.save()
        test_user = profile_factories.Profile().user
        request = self.factory.get('/request_to_join_group',
            {'group_pk': str(self.groupprofile.pk)})
        request.user = test_user
        response = views.request_to_join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "There was an error processing your request to join this group.")
        pending = PendingMember.objects.filter(user=test_user, group=self.groupprofile)
        self.assertEquals(len(pending), 0)

    def test_request_to_join_group_fails_if_already_in_group(self):
        request = self.factory.get('/request_to_join_group',
            {'group_pk': str(self.groupprofile.pk)})
        request.user = self.test_member
        response = views.request_to_join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You are already a member of this group.")
        pending = PendingMember.objects.filter(user=self.test_member, group=self.groupprofile)
        self.assertEquals(len(pending), 0)

    def test_approve_request_to_join_group_when_yes(self):
        test_user = profile_factories.Profile().user
        pending = PendingMember.objects.create(user=test_user, group=self.groupprofile,
            status="request")
        request = self.factory.get('/approve_request_to_join_group', {'approved': 'yes',
            'group_pk': str(self.groupprofile.pk), 'pending_pk': str(pending.pk)})
        request.user = self.test_admin
        response = views.approve_request_to_join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "Request approved.")
        self.assertTrue(self.groupprofile.hasMember(test_user))
        pending = PendingMember.objects.filter(user=test_user, group=self.groupprofile)
        self.assertEquals(len(pending), 0)

    def test_approve_request_to_join_group_when_no(self):
        test_user = profile_factories.Profile().user
        pending = PendingMember.objects.create(user=test_user, group=self.groupprofile,
            status="request")
        request = self.factory.get('/approve_request_to_join_group', {'approved': 'no',
            'group_pk': str(self.groupprofile.pk), 'pending_pk': str(pending.pk)})
        request.user = self.test_admin
        response = views.approve_request_to_join_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "Request denied.")
        self.assertFalse(self.groupprofile.hasMember(test_user))
        pending = PendingMember.objects.filter(user=test_user, group=self.groupprofile)
        self.assertEquals(len(pending), 0)

    def test_approve_invite_to_group_when_yes(self):
        test_user = profile_factories.Profile().user
        pending = PendingMember.objects.create(user=test_user, group=self.groupprofile,
            status="invite", inviter=self.test_owner)
        request = self.factory.get('/approve_invite_to_group', {'approved': 'yes',
            'group_pk': str(self.groupprofile.pk), 'pending_pk': str(pending.pk)})
        request.user = test_user
        response = views.approve_invite_to_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You have joined the group.")
        self.assertTrue(self.groupprofile.hasMember(test_user))
        pending = PendingMember.objects.filter(user=test_user, group=self.groupprofile)
        self.assertEquals(len(pending), 0)

    def test_approve_invite_to_group_when_no(self):
        test_user = profile_factories.Profile().user
        pending = PendingMember.objects.create(user=test_user, group=self.groupprofile,
            status="invite", inviter=self.test_owner)
        request = self.factory.get('/approve_invite_to_group', {'approved': 'no',
            'group_pk': str(self.groupprofile.pk), 'pending_pk': str(pending.pk)})
        request.user = test_user
        response = views.approve_invite_to_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You have declined to join the group.")
        self.assertFalse(self.groupprofile.hasMember(test_user))
        pending = PendingMember.objects.filter(user=test_user, group=self.groupprofile)
        self.assertEquals(len(pending), 0)

    def test_change_admin_fails_if_not_owner(self):
        request = self.factory.get('/change_admin', {'action': 'add',
            'group_pk': str(self.groupprofile.pk), 'user_pk': str(self.test_member.pk)})
        request.user = self.test_admin
        response = views.change_admin(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "You do not have permission to add or remove admins.")
        self.assertFalse(self.groupprofile.hasAdmin(self.test_member))

    def test_change_admin_lets_owner_make_member_admin(self):
        request = self.factory.get('/change_admin', {'action': 'add',
            'group_pk': str(self.groupprofile.pk), 'user_pk': str(self.test_member.pk)})
        request.user = self.test_owner
        response = views.change_admin(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "User added as admin.")
        self.assertTrue(self.groupprofile.hasAdmin(self.test_member))

    def test_change_admin_lets_owner_make_admin_into_regular_member(self):
        request = self.factory.get('/change_admin', {'action': 'remove',
            'group_pk': str(self.groupprofile.pk), 'user_pk': str(self.test_admin.pk)})
        request.user = self.test_owner
        response = views.change_admin(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'], "User removed as admin.")
        self.assertFalse(self.groupprofile.hasAdmin(self.test_admin))
        self.assertTrue(self.groupprofile.hasMember(self.test_admin))

    def test_invite_to_group_works_for_multiple_invites(self):
        riley = User.objects.create(username="riley")
        glory = User.objects.create(username="glory")
        request = self.factory.get('/invite_to_group', {'usernames[]': ['riley', 'glory'],
            'group_pk': str(self.groupprofile.pk)})
        request.user = self.test_owner
        response = views.invite_to_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'][:17], "You have invited ")
        pending = PendingMember.objects.filter(group=self.groupprofile)
        self.assertEquals(len(pending), 2)

    def test_invite_to_group_doesnt_invite_members(self):
        riley = User.objects.create(username="riley")
        glory = User.objects.create(username="glory")
        self.groupprofile.addMember(glory)
        request = self.factory.get('/invite_to_group', {'usernames[]': ['riley', 'glory'],
            'group_pk': str(self.groupprofile.pk)})
        request.user = self.test_owner
        response = views.invite_to_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'][:17], "You have invited ")
        pending = PendingMember.objects.filter(group=self.groupprofile)
        self.assertEquals(len(pending), 1)

    def test_invite_to_group_doesnt_invite_pending(self):
        riley = User.objects.create(username="riley")
        glory = User.objects.create(username="glory")
        PendingMember.objects.create(group=self.groupprofile, user=glory, status="request")
        request = self.factory.get('/invite_to_group', {'usernames[]': ['riley', 'glory'],
            'group_pk': str(self.groupprofile.pk)})
        request.user = self.test_owner
        response = views.invite_to_group(request)
        result = json.loads(response.content)
        self.assertEqual(result['message'][:17], "You have invited ")
        pending = PendingMember.objects.filter(group=self.groupprofile)
        self.assertEquals(len(pending), 2)
        pending = PendingMember.objects.filter(group=self.groupprofile, status="invite")
        self.assertEquals(len(pending), 1)