from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils import timezone

from django.contrib.auth.models import User

from actions.models import Action
from mysite.utils import (PRIVACY_CHOICES, PRIORITY_CHOICES, INDIVIDUAL_STATUS_CHOICES,
    PRIVACY_DEFAULT_CHOICES, check_privacy, get_global_privacy_default)

class Profile(models.Model):
    """Stores a single user profile"""
    user = models.OneToOneField(User, unique=True)
    verified = models.BooleanField(default=False)
    description = models.CharField(max_length=500, blank=True, null=True)  # TODO Rich text?
    location = models.CharField(max_length=140, blank=True, null=True)
    links = models.CharField(max_length=400, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    connections = models.ManyToManyField('self',
                                        through='Relationship',
                                        symmetrical=False,
                                        related_name='connected_to')
    actions = models.ManyToManyField(Action, through='ProfileActionRelationship')
    # privacy default is inh == inherit
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')

    def __unicode__(self):
        return self.user.username

    def get_cname(self):
        class_name = 'Profile'
        return class_name

    def get_name(self):
        if self.user.first_name not in [None, ""]:
            return self.user.first_name + " " + self.user.last_name
        else:
            return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'slug': self.user.username })

    def get_edit_url(self):
        return reverse('edit_profile', kwargs={'pk': self.pk })

    def get_relationship_given_profile(self, profile):
        rel = Relationship.objects.filter(person_A=self, person_B=profile)
        if rel:
            return rel[0]
        rel = Relationship.objects.filter(person_A=profile, person_B=self)
        if rel:
            return rel[0]
        return None

    def get_par_given_action(self, action):
        try:
            par = ProfileActionRelationship.objects.get(profile=self, action=action)
            return par
        except:
            return None

    def get_followers(self):
        followers = []
        # This should be something like for rel in self.relationship_set.all()
        # but it doesn't seem to work
        for person in self.connections.all():
            rel = self.get_relationship_given_profile(person)
            if rel.target_follows_current_profile(self):
                followers.append(person.pk)
        return Profile.objects.filter(pk__in=followers)

    def get_location(self):
        if self.location:
            return self.location
        else:
            return "Unknown"

    def vet_actions(self, potential_actions, user, privacy=True, status=True):
        actions = []
        for action in potential_actions:
            obj_to_check = ProfileActionRelationship.objects.filter(profile=self, action=action).first()
            if not obj_to_check: # Created actions won't have a par
                obj_to_check = action
            if privacy and not check_privacy(obj_to_check, user):
                continue
            if status and obj_to_check.get_status() not in ["Suggested to you", "Accepted"]:
                continue
            actions.append(action)
        return actions

    def get_most_recent_actions_created(self, user):
        actions = self.vet_actions(self.user.action_set.all(), user, status=False)
        if len(actions) > 5:
            return actions[-5:]
        return actions

    def get_most_recent_actions_tracked(self, user):
        actions = self.vet_actions(self.actions.all(), user)
        if len(actions) > 5:
            return actions[-5:]
        return actions

    def get_open_actions(self, user):
        actions = self.vet_actions(self.actions.all(), user, privacy=False)
        return actions

    # Add methods to save and access links as json objects

    # Add links to get specific kinds of links, so that Twitter for instance can be displayed with the
    # Twitter image

    # Add methods to facilitate viewing on friendfeeds

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        PrivacyDefaults.objects.create(profile=profile)
post_save.connect(create_user_profile, sender=User)

class Relationship(models.Model):
    """Stores a single relationship"""
    person_A = models.ForeignKey(Profile, related_name='relationship_A')
    person_B = models.ForeignKey(Profile, related_name='relationship_B')
    A_follows_B = models.BooleanField(default=False)
    B_follows_A = models.BooleanField(default=False)
    A_accountable_B = models.BooleanField(default=False)
    B_accountable_A = models.BooleanField(default=False)
    A_mutes_B = models.BooleanField(default=False)
    B_mutes_A = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Relationship of : %s and %s' % (self.person_A, self.person_B)

    def get_other(self, profile):
        if profile == self.person_A:
            return self.person_B
        if profile == self.person_B:
            return self.person_A
        return None

    def target_follows_current_profile(self, current_profile):
        if current_profile == self.person_A:
            return self.B_follows_A
        elif current_profile == self.person_B:
            return self.A_follows_B

    def current_profile_follows_target(self, current_profile):
        if current_profile == self.person_A:
            return self.A_follows_B
        elif current_profile == self.person_B:
            return self.B_follows_A

    def toggle_following_for_current_profile(self, current_profile):
        result = None # Falsy default value inappropriate here?  Should we raise error?
        if current_profile == self.person_A:
            if self.A_follows_B == True:
                self.A_follows_B = False
                self.A_accountable_B = False  # You can't be accountable to someone you don't follow
            else:
                self.A_follows_B = True
            result = self.A_follows_B
        elif current_profile == self.person_B:
            if self.B_follows_A == True:
                self.B_follows_A = False
                self.B_accountable_A = False  # You can't be accountable to someone you don't follow
            else:
                self.B_follows_A = True
            result = self.B_follows_A
        self.save()
        return result

    def target_accountable_to_current_profile(self, current_profile):
        if current_profile == self.person_A:
            return self.B_accountable_A
        elif current_profile == self.person_B:
            return self.A_accountable_B

    def current_profile_accountable_to_target(self, current_profile):
        if current_profile == self.person_A:
            return self.A_accountable_B
        elif current_profile == self.person_B:
            return self.B_accountable_A

    def toggle_accountability_for_current_profile(self, current_profile):
        result = None  # Falsy default value inappropriate here?  Should we raise error?
        if current_profile == self.person_A:
            if self.A_accountable_B == True:
                self.A_accountable_B = False
            else:
                self.A_accountable_B = True
            result = self.A_accountable_B
        elif current_profile == self.person_B:
            if self.B_accountable_A == True:
                self.B_accountable_A = False
            else:
                self.B_accountable_A = True
            result = self.B_accountable_A
        self.save()
        return result

    def target_mutes_current_profile(self, current_profile):
        if current_profile == self.person_A:
            return self.B_mutes_A
        elif current_profile == self.person_B:
            return self.A_mutes_B

    def current_profile_mutes_target(self, current_profile):
        if current_profile == self.person_A:
            return self.A_mutes_B
        elif current_profile == self.person_B:
            return self.B_mutes_A

    def toggle_mute_for_current_profile(self, current_profile):
        result = None  # Falsy default value inappropriate here?  Should we raise error?
        if current_profile == self.person_A:
            if self.A_mutes_B == True:
                self.A_mutes_B = False
            else:
                self.A_mutes_B = True
            result = self.A_mutes_B
        elif current_profile == self.person_B:
            if self.B_mutes_A == True:
                self.B_mutes_A = False
            else:
                self.B_mutes_A = True
            result = self.B_mutes_A
        self.save()
        return result

class PrivacyDefaults(models.Model):
    """Stores default privacy"""
    profile = models.OneToOneField(Profile, unique=True, related_name="privacy_defaults")
    # global default privacy is sit == Visible sitewide
    global_default = models.CharField(max_length=3, choices=PRIVACY_DEFAULT_CHOICES, default='sit')

    def __unicode__(self):
        return u'Privacy defaults for %s' % (self.profile.user.username)

class ProfileActionRelationship(models.Model):
    """Stores relationship between a profile and an action"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    # default priority is med == medium
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    # default privacy is inh == inherit
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    # default status is ace == accepted
    status = models.CharField(max_length=3, choices=INDIVIDUAL_STATUS_CHOICES, default='ace')
    committed = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Relationship of profile %s and action %s' % (self.profile, self.action)

    def get_cname(self):
        class_name = 'ProfileActionRelationship'
        return class_name

    def get_status(self):
        if self.action.status in ["wit", "rej"]:
            return self.action.get_status_display()
        else:
            return self.get_status_display()

    # Should probably add field & method to show *who* suggested this action to you
