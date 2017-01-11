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
from slates.models import Slate
from notifications.lib import email_handlers, dailyaction

##################################
### EVENT-DRIVEN NOTIFICATIONS ###
##################################

def send_follow_user_notification(instance, follower, recipient):
    if recipient.notificationsettings.if_followed and recipient.email:
        notification = Notification.objects.create(user=recipient, event=instance)
        sent = email_handlers.follow_notification_email(recipient.profile, follower.profile)
        if sent:
            notification.sent = True
            notification.save()

def send_follow_slate_notification(instance, follower, recipient, slate):
    if recipient.notificationsettings.if_slate_followed and recipient.email:
        notification = Notification.objects.create(user=recipient, event=instance)
        sent = email_handlers.follow_slate_notification_email(recipient.profile,
            follower.profile, slate)
        if sent:
            notification.sent = True
            notification.save()

def send_follow_notification(instance):
    follower = instance.actor
    recipient = instance.target
    if type(recipient) == Slate:
        send_follow_slate_notification(instance, follower, recipient=recipient.creator,
            slate=recipient)
    else:
        send_follow_user_notification(instance, follower, recipient)

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

def send_notifications_to_users_who_follow_slate(instance):
    slate = instance.target
    recipients = slate.get_people_to_notify()
    action = instance.action_object
    action_creator = instance.action_object.creator
    for recipient in recipients:
        if (recipient != action_creator and recipient.email and recipient.notificationsettings.if_followed_slates_updated):
            notification = Notification.objects.create(user=recipient, event=instance)
            sent = email_handlers.followed_slate_updated_email(recipient.profile, action, slate)
            if sent:
                notification.sent = True
                notification.save()

def send_notification_to_action_creator(instance):
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

def send_creation_notification(instance):
    actor = instance.actor
    recipients = actor.profile.get_people_to_notify()
    for recipient in recipients:
        if (recipient.email and recipient.notificationsettings.if_followed_users_create):
            notification = Notification.objects.create(user=recipient, event=instance)
            sent = email_handlers.followed_user_creates_email(recipient.profile, actor.profile, instance.target)
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
            send_notification_to_action_creator(instance)
            send_notifications_to_users_who_follow_slate(instance)
        if instance.verb == "left comment":
            send_comment_notification(instance)
        if instance.verb == "created":
            send_creation_notification(instance)
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
    most_popular_actions = dailyaction.most_popular_actions(10) # Only needs to be generated once
    for user in User.objects.all():
        if not user.notificationsettings.daily_action or not user.email:
            continue
        action = dailyaction.generate_daily_action(user, most_popular_actions)
        if action:
            email_handlers.daily_action_email(user.profile, action)

##############################
### NON USER NOTIFICATIONS ###
##############################

def send_non_user_notifications(notifier, emails, message, instance):
    for email in emails:
        email_handlers.nonuser_email(email, notifier.profile, message, instance)
