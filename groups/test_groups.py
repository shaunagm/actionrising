from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.forms.widgets import HiddenInput

from groups.models import GroupProfile
from mysite.lib.choices import PrivacyChoices
from groups.forms import GroupForm

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
