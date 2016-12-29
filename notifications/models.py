from __future__ import unicode_literals

from django.db import models

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
