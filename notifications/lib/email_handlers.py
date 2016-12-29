from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from mysite.settings import NOTIFY_EMAIL
from mysite.lib.privacy import filter_list_for_privacy_annotated

def get_notificationsettings_url(recipient):
    url_path = reverse('manage_notifications', kwargs={'pk': recipient.user.notificationsettings.pk})
    return 'https://www.actionrising.com' + url_path

def get_toggle_notify_url(target):
    url_path = reverse('toggle_relationships', kwargs={'pk': target.pk, 'toggle_type': 'notify'})
    return 'https://www.actionrising.com' + url_path

def get_toggle_notify_for_slate_url(target):
    url_path = reverse('toggle_slate_for_profile', kwargs={'slug': target.slug, 'toggle_type': 'stop_notify'})
    return 'https://www.actionrising.com' + url_path

###########################
### EVENT-DRIVEN EMAILS ###
###########################

def follow_notification_email(recipient, follower):

    subject = "%s is now following you on ActionRising" % follower

    relationship = recipient.get_relationship_given_profile(follower)
    if relationship.current_profile_follows_target(recipient):
        follow_status = "You now follow each other."
        follows = True
    else:
        follow_status = "You don't follow them, so consider following them back."
        follows = False

    ctx = {
        # Required fields
        'preheader_text': subject,
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'recipient': recipient,
        'follower': follower,
        'follow_status': follow_status,
        'follows': follows
    }
    plain_message = render_to_string('notifications/email_templates/plain/follow.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/follow.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)

def follow_slate_notification_email(recipient, follower, slate):
    subject = "%s is following your slate on ActionRising" % follower
    ctx = {
        # Required fields
        'preheader_text': "%s is following your slate %s on ActionRising" % (follower, slate),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'follower': follower,
        'slate': slate
    }
    plain_message = render_to_string('notifications/email_templates/plain/follow_slate.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/follow_slate.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)

def action_taken_email(recipient, actor, action):

    subject = "%s is taking one of your actions on ActionRising" % actor

    trackers = filter_list_for_privacy_annotated(action.profileactionrelationship_set.all(), recipient.user)
    if trackers['total_count'] > 1:
        tracker_string = "%d people tracking it" % trackers['total_count']
    else:
        tracker_string = "%d person tracking it" % trackers['total_count']

    ctx = {
        # Required fields
        'preheader_text': "%s is taking your action '%s' on ActionRising" % (actor,
            action.title),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'tracker_string': tracker_string,
        'action': action,
        'actor': actor
    }
    plain_message = render_to_string('notifications/email_templates/plain/actiontaken.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/actiontaken.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)

def suggested_action_email(recipient, suggester, action):
    subject = "%s suggested an action for you on ActionRising" % suggester

    ctx = {
        # Required fields
        'preheader_text': "%s suggested action '%s' for you on ActionRising" % (suggester,
            action.title),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'action': action,
        'suggester': suggester,
        'accept_or_reject_url': recipient.get_suggestion_url_with_domain()
    }

    plain_message = render_to_string('notifications/email_templates/plain/suggestedaction.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/suggestedaction.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_messages)

def add_slate_email(recipient, actor, action, slate):
    subject = "%s added your action to a slate on ActionRising" % actor

    if action.slate_set.count() > 1:
        slate_string = "%s slates" % action.slate_set.count()
    else:
        slate_string = "%s slate" % action.slate_set.count()

    ctx = {
        # Required fields
        'preheader_text': "%s added your action '%s' to slate '%s' on ActionRising" % (actor,
            action.title, slate.title),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'action': action,
        'actor': actor,
        'slate': slate,
        'slate_string': slate_string
    }

    plain_message = render_to_string('notifications/email_templates/plain/addslate.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/addslate.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)

def comment_email(recipient, actor, action, comment):
    subject = "%s commented on your action on ActionRising" % actor

    ctx = {
        # Required fields
        'preheader_text': "%s commented on your action '%s' on ActionRising" % (actor,
            action.title),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'actor': actor,
        'action': action,
        'comment': comment
    }

    plain_message = render_to_string('notifications/email_templates/plain/comment.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/comment.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)

def followed_user_creates_email(recipient, actor, created_object):
    subject = "%s created a new %s on ActionRising" % (actor, created_object.get_cname())
    ctx = {
        # Required fields
        'preheader_text': "%s created a new %s '%s' on ActionRising" % (actor,
            created_object.get_cname(), created_object),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'actor': actor,
        'created_object': created_object,
        'toggle_notify_url': get_toggle_notify_url(actor.user)
    }
    plain_message = render_to_string('notifications/email_templates/plain/followed_user_created.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/followed_user_created.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)

def followed_slate_updated_email(recipient, action, slate):
    subject = "A slate you follow has a new action!"
    ctx = {
        # Required fields
        'preheader_text': "Slate %s has a new action, %s, on ActionRising" % (slate,
            action),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'slate': slate,
        'action': action,
        'toggle_notify_url': get_toggle_notify_url(slate)
    }
    plain_message = render_to_string('notifications/email_templates/plain/followed_slate_updated.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/followed_slate_updated.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)


###########################
### DAILY ACTION EMAILS ###
###########################

def daily_action_email(recipient, action):

    subject = "Your Daily Action from ActionRising"

    ctx = {
        # Required fields
        'preheader_text': "Your daily action today is '" + action.title + "'",
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'action': action
    }

    plain_message = render_to_string('notifications/email_templates/plain/dailyaction.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/dailyaction.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)

###########################
### EMAILS TO NON-USERS ###
###########################

def request_email(invite):
    subject = "Your request to join ActionRising has been approved"

    ctx = {
        # Required fields
        'preheader_text': subject,
        # Email-specific fields
        'invite': invite
    }

    plain_message = render_to_string('notifications/email_templates/plain/request.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/request.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [invite.email], html_message=html_message)

def invite_email(invite):
    subject = "%s is inviting you to join ActionRising" % invite.get_inviter_string()

    ctx = {
        # Required fields
        'preheader_text': subject,
        # Email-specific fields
        'invite': invite
    }

    plain_message = render_to_string('notifications/email_templates/plain/invite.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/invite.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [invite.email], html_message=html_message)

def invite_notification_email(invite):
    if invite.self_submitted:
        return request_email(invite)
    else:
        return invite_email(invite)

def nonuser_email(recipient_email, notifier, message, instance):
    subject = "%s wants you to take action on ActionRising" % (notifier)

    if instance.get_cname == "Slate":
        notification_string = "a slate of actions they're taking"
    else:
        notification_string = "an action they're taking"

    ctx = {
        # Required fields
        'preheader_text': subject,
        # Email-specific fields
        'notifier': notifier,
        'message': message,
        'instance': instance,
        'notification_string': notification_string,
        'request_invite_url': 'https://www.actionrising.com/invites/request-account'
    }

    plain_message = render_to_string('notifications/email_templates/plain/nonuser.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/nonuser.html', ctx)
    return send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient_email], html_message=html_message)
