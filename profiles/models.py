from __future__ import unicode_literals

import json, datetime
from random import shuffle
from itertools import chain

from actstream import action
from django.db import models
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from ckeditor.fields import RichTextField
from mysite.settings import PRODUCTION_DOMAIN
from actstream.actions import follow, unfollow
from actions.models import Action, District, Slate
from notifications.models import NotificationSettings, DailyActionSettings
from mysite.lib.choices import (PRIVACY_CHOICES, PRIORITY_CHOICES, INDIVIDUAL_STATUS_CHOICES,
    PRIVACY_DEFAULT_CHOICES)
from mysite.lib.utils import disable_for_loaddata
from profiles.lib.status_helpers import close_commitment_when_PAR_is_closed, reopen_commitment_when_par_is_reopened

class Profile(models.Model):
    """Stores a single user profile"""
    user = models.OneToOneField(User, unique=True)
    verified = models.BooleanField(default=False)
    description = RichTextField(max_length=2500, blank=True, null=True)  # TODO Rich text?
    location = models.CharField(max_length=140, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    district = models.ForeignKey(District, blank=True, null=True)
    links = models.CharField(max_length=400, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    connections = models.ManyToManyField('self',
                                        through='Relationship',
                                        symmetrical=False,
                                        related_name='connected_to')
    actions = models.ManyToManyField(Action, through='ProfileActionRelationship')
    slates = models.ManyToManyField(Slate, through='ProfileSlateRelationship')
    # privacy default is inh == inherit
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    current_privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='fol')

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.pk and self.privacy != "inh" and self.privacy != self.current_privacy:
            self.current_privacy = self.privacy
        super(Profile, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'Profile'
        return class_name

    def get_name(self):
        if self.user.first_name not in [None, ""]:
            return self.user.first_name + " " + self.user.last_name
        else:
            return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.user.pk })

    def get_absolute_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_absolute_url()

    def get_edit_url(self):
        return reverse('edit_profile', kwargs={'pk': self.pk })

    def get_edit_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_edit_url()

    def get_suggestion_url_with_domain(self):
        return PRODUCTION_DOMAIN + reverse('suggested', kwargs={'pk': self.user.pk })

    def refresh_current_privacy(self):
        if self.privacy == "inh":
            self.current_privacy = self.privacy_defaults.global_default
        else:
            self.current_privacy = self.privacy
        self.save()

    def get_user_privacy(self):
        return self.privacy_defaults.global_default

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

    def get_psr_given_slate(self, slate):
        try:
            return ProfileSlateRelationship.objects.get(profile=self, slate=slate)
        except:
            return None

    def get_followers(self):
        followers = []
        # This should be something like for rel in self.relationship_set.all()
        # but it doesn't seem to work
        for person in self.get_connected_people():
            rel = self.get_relationship_given_profile(person)
            if rel.target_follows_current_profile(self):
                followers.append(person.pk)
        return Profile.objects.filter(pk__in=followers)

    def get_people_user_follows(self):
        people_followed = []
        for person in self.get_connected_people():
            rel = self.get_relationship_given_profile(person)
            if rel.current_profile_follows_target(self):
                people_followed.append(person.pk)
        return Profile.objects.filter(pk__in=people_followed)

    def get_people_to_notify(self):
        notify = []
        for person in self.get_connected_people():
            rel = self.get_relationship_given_profile(person)
            if rel.target_notified_of_current_profile(self):
                notify.append(person.pk)
        return [profile.user for profile in Profile.objects.filter(pk__in=notify)]

    def get_location(self):
        if self.location:
            return self.location
        else:
            return "Unknown"

    def get_most_recent_actions_created(self):
        actions = self.user.action_set.filter(status__in=["rea", "fin"]).order_by('-date_created')
        if len(actions) > 5:
            return actions[:5]
        return actions

    def get_most_recent_actions_tracked(self):
        actions = [par.action for par in self.profileactionrelationship_set.all() if par.action.status in ["rea", "fin"]]
        if len(actions) > 5:
            return actions[:5]
        return actions

    def get_open_actions(self):
        actions = [par.action for par in self.profileactionrelationship_set.filter(status="ace")]
        return [action for action in actions if action.status == "rea"]

    def get_open_pars(self):
        return ProfileActionRelationship.objects.filter(profile=self, status="ace")

    def get_suggested_actions(self):
        return ProfileActionRelationship.objects.filter(profile=self, status="sug")

    def get_suggested_actions_count(self):
        return len(self.get_suggested_actions())

    def get_connected_people(self):
        for_a = [rel.person_B for rel in Relationship.objects.filter(person_A=self)]
        for_b = [rel.person_A for rel in Relationship.objects.filter(person_B=self)]
        return list(chain(for_a, for_b))

    def get_list_of_relationships(self):
        people = []
        for person in self.get_connected_people():
            rel = self.get_relationship_given_profile(person)
            you_follow = rel.current_profile_follows_target(self)
            follows_you = rel.target_follows_current_profile(self)
            muted = rel.current_profile_mutes_target(self)
            profile = rel.get_other(self)
            people.append({'user': profile.user, 'mutual': follows_you and you_follow,
                'follows_you': follows_you, 'you_follow': you_follow, 'muted': muted})
        return people

    def get_people_tracking(self):
        people = []
        for person in self.get_connected_people():
            rel = self.get_relationship_given_profile(person)
            if rel.current_profile_follows_target(self) and not rel.current_profile_mutes_target(self):
                people.append(person.user)
        return people

    def get_percent_finished(self):
        total_count = 0
        finished_count = 0
        for action in self.profileactionrelationship_set.all():
            total_count += 1
            if action.status == "don":
                finished_count += 1
        if total_count == 0:
            return 0
        return float(finished_count)/float(total_count)*100

    def get_action_streak(self):
        streak_length = 0
        today = datetime.datetime.now().date()
        dates = [action.date_finished.date() for action in self.profileactionrelationship_set.all() if action.date_finished]
        while True:
            if today in dates:
                streak_length += 1
                today = today - datetime.timedelta(days=1)
            else:
                break
        return streak_length

    def get_friends_actions(self):
        actions = []
        # Get actions made by people you follow
        people = self.get_people_user_follows()
        for person in people:
            for action in person.user.action_set.filter(status="rea"):
                actions.append(action)
        # Get actions in slates you follow
        for slate in self.slates.all():
            for sar in slate.slateactionrelationship_set.all():
                if sar.action.status == "rea":
                    actions.append(sar.action)
        return actions

    # Add methods to save and access links as json objects

    # Add links to get specific kinds of links, so that Twitter for instance can be displayed with the
    # Twitter image

@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        PrivacyDefaults.objects.create(profile=profile)
        NotificationSettings.objects.create(user=instance)
        DailyActionSettings.objects.create(user=instance)
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
    A_notified_of_B = models.BooleanField(default=False)
    B_notified_of_A = models.BooleanField(default=False)

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
                unfollow(self.person_A.user, self.person_B.user)
            else:
                self.A_follows_B = True
                follow(self.person_A.user, self.person_B.user, actor_only=False)
            result = self.A_follows_B
        elif current_profile == self.person_B:
            if self.B_follows_A == True:
                self.B_follows_A = False
                self.B_accountable_A = False  # You can't be accountable to someone you don't follow
                unfollow(self.person_B.user, self.person_A.user)
            else:
                self.B_follows_A = True
                follow(self.person_B.user, self.person_A.user, actor_only=False)
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

    def target_notified_of_current_profile(self, current_profile):
        if current_profile == self.person_A:
            return self.B_notified_of_A
        elif current_profile == self.person_B:
            return self.A_notified_of_B

    def current_profile_notified_of_target(self, current_profile):
        if current_profile == self.person_A:
            return self.A_notified_of_B
        elif current_profile == self.person_B:
            return self.B_notified_of_A

    def toggle_notified_of_for_current_profile(self, current_profile):
        result = None  # Falsy default value inappropriate here?  Should we raise error?
        if current_profile == self.person_A:
            if self.A_notified_of_B == True:
                self.A_notified_of_B = False
            else:
                self.A_notified_of_B = True
            result = self.A_notified_of_B
        elif current_profile == self.person_B:
            if self.B_notified_of_A == True:
                self.B_notified_of_A = False
            else:
                self.B_notified_of_A = True
            result = self.B_notified_of_A
        self.save()
        return result

class PrivacyDefaults(models.Model):
    """Stores default privacy"""
    profile = models.OneToOneField(Profile, unique=True, related_name="privacy_defaults")
    # global default privacy is sit == Visible sitewide
    global_default = models.CharField(max_length=3, choices=PRIVACY_DEFAULT_CHOICES, default='pub')

    def __unicode__(self):
        return u'Privacy defaults for %s' % (self.profile.user.username)

    def save(self, *args, **kwargs):
        if self.pk:
            orig = PrivacyDefaults.objects.get(pk=self.pk)
            if orig.global_default != self.global_default:
                self.save_dependencies()
        else:
            self.save_dependencies()
        super(PrivacyDefaults, self).save(*args, **kwargs)

    def save_dependencies(self):
        self.profile.current_privacy = self.global_default
        self.profile.save()
        for slate in self.profile.user.slate_set.all():
            slate.current_privacy = self.global_default
            slate.save()
        for action in self.profile.user.action_set.all():
            action.current_privacy = self.global_default
            action.save()

class ProfileActionRelationship(models.Model):
    """Stores relationship between a profile and an action"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    # default priority is med == medium
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    # default status is ace == accepted
    status = models.CharField(max_length=3, choices=INDIVIDUAL_STATUS_CHOICES, default='ace')
    committed = models.BooleanField(default=False)
    last_suggester = models.ForeignKey(User, blank=True, null=True)
    suggested_by = models.CharField(max_length=500, blank=True, null=True)
    notes = models.CharField(max_length=2500, blank=True, null=True)
    date_accepted = models.DateTimeField(default=timezone.now)
    date_finished = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u'Relationship of profile %s and action %s' % (self.profile, self.action)

    def save(self, *args, **kwargs):
        if self.pk:
            orig = ProfileActionRelationship.objects.get(pk=self.pk)
            if orig.status != "clo" and self.status == "clo":
                close_commitment_when_PAR_is_closed(self)
            if orig.status == "rea" and self.status != "rea":
                reopen_commitment_when_par_is_reopened(self)
        super(ProfileActionRelationship, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'ProfileActionRelationship'
        return class_name

    def get_status(self):
        if self.action.status in ["wit", "rej"]:
            return self.action.get_status_display()
        else:
            return self.get_status_display()

    def get_suggesters(self):
        if self.suggested_by is not None:
            return json.loads(self.suggested_by)
        return []

    def get_suggesters_html(self):
        suggesters = ""
        for user in self.get_suggesters():
            user_obj = User.objects.get(username=user)
            suggesters += "<a href='" + user_obj.profile.get_absolute_url() + "'>" + user_obj.username + "</a>, "
        return suggesters[0:-2]

    def set_suggesters(self, suggesters):
        self.suggested_by = json.dumps(suggesters)
        self.save()

    def add_suggester(self, suggester):
        suggesters = self.get_suggesters()
        if suggester not in suggesters:
            suggesters.append(suggester)
        self.set_suggesters(suggesters)

# I think we just want to track PAR & PSR for now.
@disable_for_loaddata
def par_handler(sender, instance, created, **kwargs):
    if created:
        if instance.status == "sug":
            action.send(instance.last_suggester, verb='suggested action', action_object=instance.action, target=instance.profile.user)
        else:
            action.send(instance.profile.user, verb='is taking action', target=instance.action)
    if instance.status == "don":
        action.send(instance.profile.user, verb='completed action', target=instance.action)
post_save.connect(par_handler, sender=ProfileActionRelationship)

class ProfileSlateRelationship(models.Model):
    """Stores relationship between a profile and a slate"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    slate = models.ForeignKey(Slate, on_delete=models.CASCADE)
    notify_of_additions = models.BooleanField(default=True)
