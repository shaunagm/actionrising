from django.test import TestCase
from django.utils import timezone

from groups.models import GroupProfile

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
        self.assertTrue(test_group.group.name, "a-test-groupname")
