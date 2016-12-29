from __future__ import unicode_literals

import json, ast

from django.db import models
from mysite.lib.choices import DAILY_ACTION_SOURCE_CHOICES
from actstream.models import Action
from django.contrib.auth.models import User

class NotificationSettings(models.Model):
    user = models.OneToOneField(User, unique=True)
    # Notification Mode 1: Daily Action
    daily_action = models.BooleanField(default=True)
    use_own_actions_if_exist = models.BooleanField(default=True)
    # Notification Mode 2: Weekly Summary
    weekly_summary = models.BooleanField(default=False)
    # Notification Mode 3: Event Driven
    if_followed = models.BooleanField(default=True)
    if_slate_followed = models.BooleanField(default=True)
    if_actions_followed = models.BooleanField(default=True)
    if_comments_on_my_actions = models.BooleanField(default=True)
    if_my_actions_added_to_slate = models.BooleanField(default=True)
    if_suggested_action = models.BooleanField(default=True)
    # Notification Mode 4: Followed users & slates
    if_followed_users_create = models.BooleanField(default=True)
    if_followed_slates_updated =  models.BooleanField(default=True)

    def __unicode__(self):
        return u'Notification Settings for %s' % (self.user.username)

class Notification(models.Model):
    user =  models.ForeignKey(User) # Person to notify
    event = models.ForeignKey(Action)
    sent = models.BooleanField(default=False)
    # probably need an additional field to mark something as permanent failure

    def __unicode__(self):
        sent_status = "sent" if self.sent else "unsent"
        return u'Notify %s of %s (%s)' % (self.user.username, self.event, sent_status)

class DailyActionSettings(models.Model):
    user = models.OneToOneField(User, unique=True)
    recently_seen = models.CharField(max_length=50, blank=True, null=True)
    # Sources
    my_own_actions = models.CharField(max_length=5, choices=DAILY_ACTION_SOURCE_CHOICES,
        default='few')
    my_friends_actions = models.CharField(max_length=5, choices=DAILY_ACTION_SOURCE_CHOICES,
        default='few')
    popular_actions = models.CharField(max_length=5, choices=DAILY_ACTION_SOURCE_CHOICES,
        default='few')
    # Filters
    duration_filter = models.CharField(max_length=200, blank=True, null=True)
    duration_filter_on = models.BooleanField(default=False)
    action_type_filter = models.CharField(max_length=200, blank=True, null=True)
    action_type_filter_on = models.BooleanField(default=False)
    action_topic_filter = models.CharField(max_length=200, blank=True, null=True)
    action_topic_filter_on = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Daily Action Settings for %s' % (self.user.username)

    def get_recently_seen_pks(self):
        if self.recently_seen:
            return json.loads(self.recently_seen)
        return []

    def set_recently_seen_pks(self, pks):
        self.recently_seen = json.dumps(pks)
        self.save()

    def add_recently_seen_action(self, action):
        pks = self.get_recently_seen_pks()
        if len(pks) > 10 or action is None:
            # If our filters/sources are giving us few actions, pop a pk regardless
            pks.pop(0)
        if action:
            pks.append(action.pk)
        self.set_recently_seen_pks(pks)

    def get_duration_filter_shortnames(self):
        return ast.literal_eval(self.duration_filter)

    def get_topic_filter_pks(self):
        pks = ast.literal_eval(self.action_topic_filter)
        return [int(pk) for pk in pks]

    def get_type_filter_pks(self):
        pks = ast.literal_eval(self.action_type_filter)
        return [int(pk) for pk in pks]
