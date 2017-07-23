from __future__ import unicode_literals

from django.contrib.auth.models import Group, User
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from mysite.lib.utils import groupname_helper

from ckeditor.fields import RichTextField
from guardian.shortcuts import assign_perm, remove_perm

from mysite.lib.choices import PrivacyChoices
from mysite.lib.privacy import privacy_tests

class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    owner = models.ForeignKey(User)
    groupname = models.CharField(max_length=140)
    privacy = models.CharField(max_length=10, choices=PrivacyChoices.group_choices(),
        default=PrivacyChoices.public)
    description = RichTextField(max_length=4000, blank=True, null=True)
    summary = models.CharField(max_length=300, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        permissions = (
            ('admin_group', 'Administer group'),
        )

    def __unicode__(self):
        return self.groupname

    def save(self, *args, **kwargs):
        if not self.pk: # if being created
            self.group = Group.objects.create(name=groupname_helper(self.groupname))
        super(GroupProfile, self).save(*args, **kwargs)
        if not self.hasAdmin(self.owner):
            self.addAdmin(self.owner)

    def hasMember(self, user):
        return self.group.user_set.filter(username=user.username).exists()

    def hasAdmin(self, user):
        '''Checks if user is in group and has the admin permission'''
        member = self.group.user_set.filter(username=user.username).first()
        if member:
            return member.has_perm('groups.admin_group', self)
        return False

    def addMember(self, user):
        self.group.user_set.add(user)

    def addAdmin(self, user):
        self.addMember(user)
        assign_perm('admin_group', user, self)

    def removeMember(self, user):
        if self.hasAdmin(user):
            remove_perm('admin_group', user, self)
        self.group.user_set.remove(user)

    def removeAdmin(self, user):
        remove_perm('admin_group', user, self)

    def get_absolute_url(self):
        return reverse('group', kwargs={'slug': self.groupname})

    def get_edit_url(self):
        return reverse('edit_group', kwargs={'slug': self.groupname})

    def get_admin_url(self):
        return reverse('admin_group', kwargs={'slug': self.groupname})

    def is_visible_to(self, viewer, follows_user=None):
        return privacy_tests[self.privacy](self, viewer, follows_user)

    def get_members(self):
        return User.objects.filter(groups__name=self.group.name)

