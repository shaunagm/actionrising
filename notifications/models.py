from __future__ import unicode_literals

import random

from django.utils.translation import ugettext as _
from django.db import models
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django_comments.models import Comment
from django.db.models import Count

from actstream import action
from actstream.models import following, followers
from actstream.models import Action
from actions.models import Action as ActionRisingAction # TODO: Fix name collision
from django.contrib.auth.models import User
from mysite.utils import disable_for_loaddata, check_privacy, check_privacy_given_setting
from mysite.settings import NOTIFY_EMAIL
from email_templates import (generate_follow_email, generate_add_to_slate_email,
    generate_take_action_email, generate_comment_email, generate_daily_action_email)

class NotificationSettings(models.Model):
    user = models.OneToOneField(User, unique=True)
    # Notification Mode 1: Daily Action
    daily_action = models.BooleanField(default=True)
    use_own_actions_if_exist = models.BooleanField(default=True)
    # Notification Mode 2: Weekly Summary
    weekly_summary = models.BooleanField(default=False)
    # Notification Mode 3: Event Driven
    if_followed = models.BooleanField(default=True)
    if_actions_followed = models.BooleanField(default=True)
    if_comments_on_my_actions = models.BooleanField(default=True)
    if_my_actions_added_to_slate = models.BooleanField(default=True)

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

### EVENT-DRIVEN NOTIFICATIONS

def send_follow_notification(instance):
    follower = instance.actor
    target = instance.target
    if target.notificationsettings.if_followed and target.email:
        notification = Notification.objects.create(user=target, event=instance)
        email_subj, email_message, html_message = generate_follow_email(follower.profile, target.profile)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [target.email],
            fail_silently=False, html_message=html_message)
        if sent:
            notification.sent = True
            notification.save()

def send_take_action_notification(instance):
    action_creator = instance.target.creator
    if action_creator.notificationsettings.if_actions_followed and action_creator.email:
        actor_privacy_setting = instance.actor.profile.privacy_defaults.global_default
        if not check_privacy_given_setting(actor_privacy_setting, instance.actor, action_creator):
            return
        notification = Notification.objects.create(user=action_creator, event=instance)
        email_subj, email_message, html_message = generate_take_action_email(action_creator.profile, instance)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [action_creator.email],
            fail_silently=False, html_message=html_message)
        if sent:
            notification.sent = True
            notification.save()

def send_added_to_slate_notification(instance):
    action_creator = instance.action_object.creator
    if action_creator.notificationsettings.if_my_actions_added_to_slate and action_creator.email:
        actor_privacy_setting = instance.actor.profile.privacy_defaults.global_default
        if not check_privacy_given_setting(actor_privacy_setting, instance.actor, action_creator):
            return
        if not check_privacy(instance.target, action_creator):
            return
        notification = Notification.objects.create(user=action_creator, event=instance)
        email_subj, email_message, html_message = generate_add_to_slate_email(action_creator.profile, instance)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [action_creator.email],
            fail_silently=False, html_message=html_message)
        if sent:
            notification.sent = True
            notification.save()

def send_comment_notification(instance):
    action_creator = instance.target.creator
    if action_creator.notificationsettings.if_comments_on_my_actions and action_creator.email:
        notification = Notification.objects.create(user=action_creator, event=instance)
        email_subj, email_message, html_message = generate_comment_email(instance)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [action_creator.email],
            fail_silently=False, html_message=html_message)
        if sent:
            notification.sent = True
            notification.save()

@disable_for_loaddata
def create_event_driven_notification(sender, instance, created, **kwargs):
    if created:
        if instance.verb == "started following":
            send_follow_notification(instance)
        if instance.verb == "is taking action":
            send_take_action_notification(instance)
        if instance.verb == "added" and instance.target.get_cname() == "Slate":
            send_added_to_slate_notification(instance)
        if instance.verb == "commented on":
            send_comment_notification(instance)
post_save.connect(create_event_driven_notification, sender=Action)

@disable_for_loaddata
def comment_handler(sender, instance, created, **kwargs):
    if created:
        action.send(instance.user, verb="commented on", target=instance.content_object)
post_save.connect(comment_handler, sender=Comment)

### DAILY ACTION NOTIFICATIONS

def send_daily_actions():
    popular_actions = ActionRisingAction.objects.filter(status="rea").annotate(tracker_count=Count('profileactionrelationship')).order_by('-tracker_count')
    top_five_actions = popular_actions[:5] if len(popular_actions) > 5 else popular_actions
    for user in User.objects.all():
        if not user.notificationsettings.daily_action or not user.email:
            continue
        actions = user.profile.get_open_actions() if user.notificationsettings.use_own_actions_if_exist else []
        if actions:
            email_subj, email_message, html_message = generate_daily_action_email(random.choice(actions), "yours", user.profile)
        else:
            email_subj, email_message, html_message = generate_daily_action_email(random.choice(top_five_actions), "top", user.profile)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [user.email], fail_silently=False, html_message=html_message)

# TODO: Weekly summary: chron job sometime on weekend, calculates your activity and sitewide activity,
# sends.
