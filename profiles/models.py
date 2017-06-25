from __future__ import division, unicode_literals

import json, datetime

import actstream
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from ckeditor.fields import RichTextField
from mysite.settings import PRODUCTION_DOMAIN
from actstream.actions import follow, unfollow
from actions.models import Action
from slates.models import Slate
from notifications.models import NotificationSettings, DailyActionSettings
from mysite.lib.choices import (PrivacyChoices, PriorityChoices, StatusChoices, ToDoStatusChoices)
from mysite.lib.privacy import privacy_tests
from mysite.lib.utils import disable_for_loaddata
from profiles.lib import status_helpers

class Profile(models.Model):
    """Stores a single user profile"""
    user = models.OneToOneField(User, unique=True)
    verified = models.BooleanField(default=False)
    description = RichTextField(max_length=2500, blank=True, null=True)  # TODO Rich text?
    links = models.CharField(max_length=400, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    connections = models.ManyToManyField('self',
                                        through='Relationship',
                                        symmetrical=False,
                                        related_name='connected_to')
    actions = models.ManyToManyField(Action, through='ProfileActionRelationship')
    slates = models.ManyToManyField(Slate, through='ProfileSlateRelationship')
    privacy = models.CharField(max_length=10, choices=PrivacyChoices.choices, default=PrivacyChoices.inherit)
    current_privacy = models.CharField(max_length=10, choices=PrivacyChoices.choices, default=PrivacyChoices.follows)

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.refresh_current_privacy()
        super(Profile, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'Profile'
        return class_name

    def get_creator(self):
        return self.user

    def get_profile(self):
        return self

    def named(self):
        return True

    def get_full_name(self):
        names = []
        if self.user.first_name not in [None, ""]:
            names.append(self.user.first_name)
        if self.user.last_name not in [None, ""]:
            names.append(self.user.last_name)
        return " ".join(names)

    def get_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'slug': self.user.username})

    def get_absolute_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_absolute_url()

    def get_edit_url(self):
        return reverse('edit_profile')

    def get_edit_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_edit_url()

    def get_suggestion_url_with_domain(self):
        return PRODUCTION_DOMAIN + reverse('suggested')

    def refresh_current_privacy(self):
        try:
            if self.privacy == PrivacyChoices.inherit:
                self.current_privacy = self.privacy_defaults.global_default
            else:
                self.current_privacy = self.privacy
        except PrivacyDefaults.DoesNotExist:
            PrivacyDefaults._meta.get_field('global_default').get_default()

    def get_user_privacy(self):
        return self.privacy_defaults.global_default

    def get_relationship(self, other):
        return self.get_relationship_with(other) or other.get_relationship_with(self)

    def get_relationship_with(self, other):
        '''Helper for get_relationship - looks for relationship unidirectionally.'''
        return Relationship.objects.filter(person_A=self, person_B=other).first()

    def get_par_given_action(self, action):
        return self.profileactionrelationship_set.filter(action=action).first()

    def get_psr_given_slate(self, slate):
        return self.profileslaterelationship_set.filter(slate=slate).first()

    def filter_connected_profiles(self, predicate):
        '''Helper for getting profiles with a particular kind of relationship to self.
        predicate: function taking a Relationship object and returning boolean. Used to filter Relationships.
        Returns the Profiles (besides self) associated with the Relationships that predicate is true of.'''
        profile_pks = [profile.pk for profile in self.get_connected_people()
                       if predicate(self.get_relationship(profile))]
        return Profile.objects.filter(pk__in=profile_pks)

    @cached_property
    def get_followers(self):
        return Profile.objects.filter(
            Q(relationship_A__person_B=self, relationship_A__A_follows_B=True) |
            Q(relationship_B__person_A=self, relationship_B__B_follows_A=True))

    def get_people_user_follows(self):
        return Profile.objects.filter(
            Q(relationship_A__person_B=self, relationship_A__B_follows_A=True) |
            Q(relationship_B__person_A=self, relationship_B__A_follows_B=True))

    def get_people_to_notify(self):
        profiles = self.filter_connected_profiles(lambda rel: rel.target_notified_of_current_profile(self))
        return [profile.user for profile in profiles]

    def get_most_recent_actions_created(self):
        return self.user.action_set\
            .filter(status__in=[StatusChoices.ready, StatusChoices.finished])\
            .order_by('-date_created')[:5]

    def get_most_recent_actions_tracked(self):
        return Action.objects.filter(
                profileactionrelationship__profile=self,
                profileactionrelationship__status=ToDoStatusChoices.accepted,
                status__in=[StatusChoices.ready, StatusChoices.finished])\
            .order_by('-profileactionrelationship__date_accepted')[:5]

    def get_open_actions(self):
        return Action.objects.filter(
            profileactionrelationship__profile=self,
            profileactionrelationship__status=ToDoStatusChoices.accepted,
            status=StatusChoices.ready)

    def get_open_pars(self):
        return self.profileactionrelationship_set.filter(
            status=ToDoStatusChoices.accepted,
            action__status=StatusChoices.ready)

    def get_suggested_actions(self):
        return self.profileactionrelationship_set.filter(
            status=ToDoStatusChoices.suggested,
            action__status=StatusChoices.ready).order_by('-date_accepted')

    def get_suggested_actions_count(self):
        return self.get_suggested_actions().count()

    def get_connected_people(self):
        return Profile.objects.filter(Q(relationship_A__person_B=self) | Q(relationship_B__person_A=self))

    def get_list_of_relationships(self):
        relationships = Relationship.objects.filter(Q(person_A=self) | Q(person_B=self))

        people = []
        for rel in relationships:
            you_follow = rel.current_profile_follows_target(self)
            follows_you = rel.target_follows_current_profile(self)
            muted = rel.current_profile_mutes_target(self)
            profile = rel.get_other(self)
            people.append({
                'profile': profile,
                'mutual': follows_you and you_follow,
                'follows_you': follows_you,
                'you_follow': you_follow,
                'muted': muted})
        return people

    def get_people_tracking(self):
        relationships = [(profile, self.get_relationship(profile)) for profile in self.get_connected_people()]
        return [profile.user for (profile, rel) in relationships
                if rel.current_profile_follows_target(self) and not rel.current_profile_mutes_target(self)]

    def get_percent_finished(self):
        total_count = 0
        finished_count = 0
        for action in self.profileactionrelationship_set.all():
            total_count += 1
            if action.status == ToDoStatusChoices.done:
                finished_count += 1
        if total_count == 0:
            return 0
        return round(finished_count/total_count*100, 1)

    def get_action_streak(self):
        dates = set([action.date_finished.date() for action
                     in self.profileactionrelationship_set.all() if action.date_finished])
        today = datetime.date.today()
        # today doesn't break your streak
        most_recent_day = today if today in dates else today - datetime.timedelta(days=1)
        streak_length = 0
        while most_recent_day in dates:
            streak_length += 1
            most_recent_day -= datetime.timedelta(days=1)
        return streak_length

    def get_friends_actions(self):
        actions = []
        # Get actions made by people you follow
        people = self.get_people_user_follows()
        for person in people:
            for action in person.user.action_set.filter(status=StatusChoices.ready):
                actions.append(action)
        # Get actions in slates you follow
        for slate in self.slates.all():
            for sar in slate.slateactionrelationship_set.all():
                if sar.action.status == StatusChoices.ready:
                    actions.append(sar.action)
        return actions

    def is_visible_to(self, viewer, follows_user = None):
        return privacy_tests[self.current_privacy](self, viewer, follows_user)

    @classmethod
    def default_sort(self, items):
        return sorted(items, key = lambda x: getattr(x, 'date_joined'), reverse = True)

    # Add methods to save and access links as json objects

    # Add links to get specific kinds of links, so that Twitter for instance can be displayed with the
    # Twitter image

@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        PrivacyDefaults.objects.create(profile=profile)  # trick into treating this as reverse one-to-one

        NotificationSettings.objects.create(user=instance)
        DailyActionSettings.objects.create(user=instance)
        # Add Location creation here, since signals aren't working for some reason
        from plugins.location_plugin.models import Location
        ctype = ContentType.objects.get_for_model(Profile)
        Location.objects.create(content_type=ctype, object_id=profile.pk)
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
    global_default = models.CharField(max_length=10, choices=PrivacyChoices.default_choices(), default=PrivacyChoices.public)

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

    def get_cname(self):
        class_name = 'PrivacyDefaults'
        return class_name

    def save_dependencies(self):
        self.profile.save()

        for slate in self.profile.user.slate_set.all():
            slate.save()

        for action in self.profile.user.action_set.all():
            action.save()


class ProfileActionRelationship(models.Model):
    """Stores relationship between a profile and an action"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.medium)
    status = models.CharField(max_length=10, choices=ToDoStatusChoices.choices, default=ToDoStatusChoices.accepted)
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
            status_helpers.change_commitment_when_par_changes(self, orig.status, self.status)
        super(ProfileActionRelationship, self).save(*args, **kwargs)

    def named(self):
        return self.action.named()

    def get_cname(self):
        class_name = 'ProfileActionRelationship'
        return class_name

    def get_creator(self):
        return self.profile.get_creator()

    def get_profile(self):
        return self.profile

    def get_status(self):
        if self.action.status == StatusChoices.withdrawn:
            return self.action.get_status_display()
        else:
            return self.get_status_display()

    def get_suggesters(self):
        if self.suggested_by is not None:
            return json.loads(self.suggested_by)
        return []

    def fetch_suggesters(self):
        return User.objects.filter(username__in=self.get_suggesters())

    def format_suggesters(self, suggesters):
        suggester_html = ["<a href='{0}'> {1} </a>".format(suggester.profile.get_absolute_url(), suggester.username)
                          for suggester in suggesters]
        return ' ,'.join(suggester_html)

    def get_suggester_html(self):
        last = self.format_suggesters([self.last_suggester])
        if len(self.get_suggesters()) > 1:
            return "{0} and <a href={1}>others</a> suggest".format(last, reverse('suggested', kwargs={'slug': self.profile.user }))
        else:
            return "{0} suggests".format(last)

    def get_suggesters_html(self):
        return self.format_suggesters(self.fetch_suggesters())

    def set_suggesters(self, suggesters):
        self.suggested_by = json.dumps(suggesters)
        self.save()

    def add_suggester(self, suggester):
        suggesters = self.get_suggesters()
        if suggester not in suggesters:
            suggesters.append(suggester)
            self.set_suggesters(suggesters)

    def is_visible_to(self, viewer, follows_user = None):
        return self.profile.is_visible_to(viewer, follows_user) and self.action.is_visible_to(viewer, follows_user)

# I think we just want to track PAR & PSR for now.
@disable_for_loaddata
def par_handler(sender, instance, created, **kwargs):
    if created:
        if instance.status == ToDoStatusChoices.suggested:
            actstream.action.send(instance.last_suggester, verb='suggested', action_object=instance.action, target=instance.profile.user)
        else:
            actstream.action.send(instance.profile.user, verb='took on', target=instance.action)
    if instance.status == ToDoStatusChoices.done:
        actstream.action.send(instance.profile.user, verb='completed', target=instance.action)

post_save.connect(par_handler, sender=ProfileActionRelationship)

class ProfileSlateRelationship(models.Model):
    """Stores relationship between a profile and a slate"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    slate = models.ForeignKey(Slate, on_delete=models.CASCADE)
    notify_of_additions = models.BooleanField(default=True)

    def __unicode__(self):
        return u'Relationship of profile %s and slate %s' % (self.profile, self.slate)

    def get_cname(self):
        class_name = 'ProfileSlateRelationship'
        return class_name

    def get_creator(self):
        return self.profile.get_creator()

    def get_profile(self):
        return self.profile

    def is_visible_to(self, viewer, follows_user = None):
        return self.profile.is_visible_to(viewer, follows_user) and self.slate.is_visible_to(viewer, follows_user)

    def named(self):
        return True
