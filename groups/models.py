from __future__ import unicode_literals

from django.contrib.auth.models import Group, User
from django.db import models
from django.utils import timezone

from ckeditor.fields import RichTextField
from guardian.shortcuts import assign_perm, remove_perm

from mysite.lib.choices import PrivacyChoices

class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    owner = models.ForeignKey(User)
    privacy = models.CharField(max_length=10, choices=PrivacyChoices.group_choices(),
        default=PrivacyChoices.public)
    description = RichTextField(max_length=4000, blank=True, null=True)
    summary = models.CharField(max_length=300, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = (
            ('admin_group', 'Administer group'),
        )

    def hasMember(self, user):
        return self.group.users.filter(username=user.username).exists()

    def hasAdmin(self, user):
        '''Checks if user is in group and has the admin permission'''
        user = self.admins.filter(username=user.username)
        if user:
            return user.has_perm('groupprofiles.admin_group', self.group)
        return False

    def addMember(self, user):
        self.group.user_set.add(user)

    def addAdmin(self, user):
        self.addMember(user)
        assign_perm('admin_group', user, self.group)

    def removeMember(self, user):
        if self.hasAdmin(user):
            remove_perm('admin_group', user, self.group)
        self.group.user_set.remove(user)

    def removeAdmin(self, user):
        remove_perm('admin_group', user, self.group)
