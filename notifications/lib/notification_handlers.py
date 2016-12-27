import random

from django.db.models import Count
from django.db.models.signals import post_save
from django.core.mail import send_mail

from django.contrib.auth.models import User
from actstream import action
from actstream.models import Action, following, followers
from django_comments.models import Comment
from mysite.settings import NOTIFY_EMAIL
from mysite.lib.utils import disable_for_loaddata
from mysite.lib.privacy import check_privacy, check_privacy_given_setting
from notifications.models import Notification
from actions.models import Action as ActionRisingAction # TODO: Fix name collision
from notifications.lib import email_handlers

##################################
### EVENT-DRIVEN NOTIFICATIONS ###
##################################

def send_follow_notification(instance):
    follower = instance.actor
    recipient = instance.target
    if recipient.notificationsettings.if_followed and recipient.email:
        notification = Notification.objects.create(user=recipient, event=instance)
        sent = email_handlers.follow_notification_email(recipient.profile, follower.profile)
        if sent:
            notification.sent = True
            notification.save()

def send_take_action_notification(instance):
    actor = instance.actor
    recipient = instance.target.creator
    action = instance.target
    privacy_access = check_privacy_given_setting(actor.profile.get_user_privacy(),
        actor.profile, recipient)
    if (recipient != actor and recipient.email and privacy_access and recipient.notificationsettings.if_actions_followed):
        notification = Notification.objects.create(user=recipient, event=instance)
        sent = email_handlers.action_taken_email(recipient.profile, actor.profile, action)
        if sent:
            notification.sent = True
            notification.save()

def send_suggestion_notification(instance):
    recipient = instance.target
    suggester = instance.actor
    if recipient.notificationsettings.if_suggested_action and recipient.email:
        notification = Notification.objects.create(user=recipient, event=instance)
        sent = email_handlers.suggested_action_email(recipient.profile, suggester.profile,
            instance.action_object)
        if sent:
            notification.sent = True
            notification.save()

def send_added_to_slate_notification(instance):
    recipient = instance.action_object.creator
    actor = instance.actor
    action = instance.action_object
    slate = instance.target
    privacy_access = check_privacy_given_setting(actor.profile.get_user_privacy(),
        actor.profile, recipient) and check_privacy(slate, recipient)
    if (recipient != actor and privacy_access and recipient.email and recipient.notificationsettings.if_my_actions_added_to_slate):
        notification = Notification.objects.create(user=recipient, event=instance)
        sent = email_handlers.add_slate_email(recipient.profile, actor.profile, action, slate)
        if sent:
            notification.sent = True
            notification.save()

def send_comment_notification(instance):
    recipient = instance.target.creator
    actor = instance.actor
    action = instance.target
    comment = instance.action_object
    if (recipient.email and recipient != actor and recipient.notificationsettings.if_comments_on_my_actions):
        notification = Notification.objects.create(user=recipient, event=instance)
        sent = email_handlers.comment_email(recipient.profile, actor.profile, action, comment)
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
        if instance.verb == "suggested action":
            send_suggestion_notification(instance)
        if instance.verb == "added" and instance.target.get_cname() == "Slate":
            send_added_to_slate_notification(instance)
        if instance.verb == "left comment":
            send_comment_notification(instance)
post_save.connect(create_event_driven_notification, sender=Action)

@disable_for_loaddata
def comment_handler(sender, instance, created, **kwargs):
    if created:
        action.send(instance.user, verb="left comment", target=instance.content_object,
            action_object=instance)
post_save.connect(comment_handler, sender=Comment)

##################################
### DAILY ACTION NOTIFICATIONS ###
##################################

def send_daily_actions():
    popular_actions = ActionRisingAction.objects.filter(status="rea").annotate(tracker_count=Count('profileactionrelationship')).order_by('-tracker_count')
    top_five_actions = popular_actions[:5] if len(popular_actions) > 5 else popular_actions
    for user in User.objects.all():
        if not user.notificationsettings.daily_action or not user.email:
            continue
        if user.notificationsettings.use_own_actions_if_exist and user.profile.get_open_actions():
            action = random.choice(user.profile.get_open_actions())
            source = "your open actions"
        else:
            action = random.choice(top_five_actions)
            source = "the most popular actions on the site"
        email_handlers.daily_action_email(user.profile, action, source)

##############################
### NON USER NOTIFICATIONS ###
##############################

def send_non_user_notifications(notifier, emails, message, instance):
    for email in emails:
        email_handlers.nonuser_email(email, notifier.profile, message, instance)
