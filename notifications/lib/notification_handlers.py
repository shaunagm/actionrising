import random

from django.db.models import Count
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.contrib.auth.models import User

from django_comments.models import Comment

from actstream import action
from actstream.models import Action, following, followers
from mysite.settings import NOTIFY_EMAIL
from mysite.lib.utils import disable_for_loaddata
from mysite.lib.privacy import check_privacy, check_privacy_given_setting
from actions.models import Action as ActionRisingAction # TODO: Fix name collision
from notifications.lib.email_templates import (generate_follow_email, generate_add_to_slate_email,
    generate_take_action_email, generate_comment_email, generate_daily_action_email,
    generate_suggestion_email, generate_non_user_email)
from notifications.models import Notification

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
    acting_user = instance.actor
    notified_user = instance.target.creator
    action = instance.target
    privacy_access = check_privacy_given_setting(acting_user.profile.get_user_privacy(),
        acting_user.profile, notified_user)
    if (notified_user != acting_user and notified_user.email and privacy_access and
        notified_user.notificationsettings.if_actions_followed):
        notification = Notification.objects.create(user=notified_user, event=instance)
        email_subj, email_message, html_message = generate_take_action_email(
            acting_user.profile, notified_user.profile, action, instance)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [notified_user.email],
            fail_silently=False, html_message=html_message)
        if sent:
            notification.sent = True
            notification.save()

def send_suggestion_notification(instance):
    target_user = instance.target
    if target_user.notificationsettings.if_suggested_action and target_user.email:
        notification = Notification.objects.create(user=target_user, event=instance)
        email_subj, email_message, html_message = generate_suggestion_email(instance, target_user.profile)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [target_user.email],
            fail_silently=False, html_message=html_message)
        if sent:
            notification.sent = True
            notification.save()

def send_added_to_slate_notification(instance):
    notified_user = instance.action_object.creator
    acting_user = instance.actor
    action = instance.action_object
    slate = instance.target
    privacy_access = check_privacy_given_setting(acting_user.profile.get_user_privacy(),
        acting_user, notified_user) and check_privacy(slate, notified_user)
    if (notified_user != acting_user and privacy_access and notified_user.email and
        notified_user.notificationsettings.if_my_actions_added_to_slate):
        notification = Notification.objects.create(user=notified_user, event=instance)
        email_subj, email_message, html_message = generate_add_to_slate_email(
            acting_user.profile, notified_user.profile, action, slate)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [notified_user.email],
            fail_silently=False, html_message=html_message)
        if sent:
            notification.sent = True
            notification.save()

def send_comment_notification(instance):
    action_creator = instance.target.creator
    if (action_creator.notificationsettings.if_comments_on_my_actions and
        action_creator.email and action_creator != instance.actor):
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
        if instance.verb == "suggested action":
            send_suggestion_notification(instance)
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

### NON USER NOTIFICATIONS

def send_non_user_notifications(notifier, emails, message, instance):
    for email in emails:
        email_subj, email_message, html_message = generate_non_user_email(notifier, message, instance)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [email],
            fail_silently=False, html_message=html_message)
