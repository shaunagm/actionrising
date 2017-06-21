import sys

from django.core.mail import send_mail
from django.template.loader import render_to_string as shadowed_render_to_string
from django.core.urlresolvers import reverse

from mysite.settings import NOTIFY_EMAIL
from mysite.constants import constants_table

EMAIL_ADDRESS = constants_table["EMAIL_ADDRESS"]


def render_to_string(path, context):
    context.update(constants_table)
    return shadowed_render_to_string(path, context)

def get_notificationsettings_url(recipient):
    url_path = reverse('manage_notifications', kwargs={'pk': recipient.user.notificationsettings.pk})
    return 'https://www.actionrising.com' + url_path

def get_toggle_notify_url(target):
    url_path = reverse('toggle_relationships', kwargs={'slug': target.username, 'toggle_type': 'notify'})
    return 'https://www.actionrising.com' + url_path

def get_toggle_notify_for_slate_url(target):
    url_path = reverse('toggle_slate_for_profile', kwargs={'slug': target.slug, 'toggle_type': 'stop_notify'})
    return 'https://www.actionrising.com' + url_path

def log_sent_mail(subject, plain_message, recipient):
    if len(plain_message) > 100:
        plain_message = plain_message[:100]
    if 'test' not in sys.argv:
        print("AR-Email Sent: ", subject, plain_message, recipient)

def log_unsent_email(subject, plain_message, recipient):
    if len(plain_message) > 100:
        plain_message = plain_message[:100]
    if 'test' not in sys.argv:
        print("AR-Email Failed to send: ", subject, plain_message, recipient)

###########################
### EVENT-DRIVEN EMAILS ###
###########################

def follow_notification_email(recipient, follower):

    subject = "%s is now following you on ActionRising" % follower

    relationship = recipient.get_relationship(follower)
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
    sent =  send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

def action_taken_email(recipient, actor, action):

    subject = "%s is taking one of your actions on ActionRising" % actor

    trackers = len(action.profileactionrelationship_set.all())
    if trackers == 1:
        tracker_string = "%d person tracking it" % trackers
    else:
        tracker_string = "%d people tracking it" % trackers

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

#############################
### ACTION CLOSING EMAILS ###
#############################

def close_action_warning_email(recipient, action):

    subject = "Your action on ActionRising is closing soon"

    ctx = {
        # Required fields
        'preheader_text': "Your action %s on ActionRising will close in 3 days" % action.title,
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'action': action
    }

    plain_message = render_to_string('notifications/email_templates/plain/close_action_warning.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/close_action_warning.html', ctx)
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

def close_action_email(recipient, action):
    subject = "Your action on ActionRising has closed"

    ctx = {
        # Required fields
        'preheader_text': "Your action %s on ActionRising has been automatically closed" % action.title,
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'action': action
    }

    plain_message = render_to_string('notifications/email_templates/plain/close_action.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/close_action.html', ctx)
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

def close_action_emails(action, closed=False):
    '''Handler to determine what, if any, emails we should send about action closures'''
    if closed and not action.deadline:
        # Only send notifications if it's a non-deadline action
        close_action_email(action.creator.profile, action)
        message = "<a href='%s'>%s</a>" % (action.get_keep_open_url_with_domain(), action.title)
        generic_admin_email("Action closed", message)
    elif action.send_warning():
        close_action_warning_email(action.creator.profile, action)

#############################
### ACCOUNTABILITY EMAILS ###
#############################

def hold_accountable_email(recipient, commitment):
    requester = commitment.profile
    action = commitment.action

    subject = "%s wants you to hold them accountable for a commitment they made " \
        "on ActionRising" % (requester)

    ctx = {
        # Required fields
        'preheader_text': "%s wants you to hold them accountable for a commitment " \
            "they made to do action %s" % (requester, action.title),
        'manage_notifications_url': get_notificationsettings_url(recipient),
        # Email-specific fields
        'action': action,
        'requester': requester,
        'message': commitment.message
    }

    plain_message = render_to_string('notifications/email_templates/plain/hold_accountable.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/hold_accountable.html', ctx)
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient.user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient.user.email)
    else:
        log_unsent_email(subject, plain_message, recipient.user.email)
    return sent

def hold_accountable_email_nonuser(recipient_email, commitment):
    requester = commitment.profile
    action = commitment.action

    subject = "%s wants you to hold them accountable for a commitment they made " \
        "on ActionRising" % requester

    ctx = {
        # Required fields
        'preheader_text': "%s wants you to hold them accountable for a commitment " \
            "they made to do action %s" % (requester, action.title),
        # Email-specific fields
        'action': action,
        'requester': requester,
        'message': commitment.message
    }

    plain_message = render_to_string('notifications/email_templates/plain/hold_accountable_nonuser.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/hold_accountable_nonuser.html', ctx)
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient_email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient_email)
    else:
        log_unsent_email(subject, plain_message, recipient_email)
    return sent

###########################
### EMAILS TO NON-USERS ###
###########################

def request_email(user, confirmation_url):
    subject = "Confirm your ActionRising account"

    ctx = {
        # Required fields
        'preheader_text': subject,
        # Email-specific fields
        'user': user,
        'confirmation_url': confirmation_url
    }

    plain_message = render_to_string('notifications/email_templates/plain/request.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/request.html', ctx)
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [user.email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, user.email)
    else:
        log_unsent_email(subject, plain_message, user.email)
    return sent

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
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient_email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient_email)
    else:
        log_unsent_email(subject, plain_message, recipient_email)
    return sent

##########################
### GENERIC USER EMAIL ###
##########################

def send_generic_email(recipient_email, generic_email):

    subject = generic_email.subject

    ctx = {
        # Required fields
        'preheader_text': generic_email.preheader_text,
        # Email-specific fields
        'email_object': generic_email
    }

    plain_message = render_to_string('notifications/email_templates/plain/generic_email.html', ctx)
    html_message = render_to_string('notifications/email_templates/html/generic_email.html', ctx)
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [recipient_email], html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, recipient_email)
    else:
        log_unsent_email(subject, plain_message, recipient_email)
    return sent

#######################
### EMAILS TO ADMIN ###
#######################

def generic_admin_email(subject, plain_message):
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, [EMAIL_ADDRESS], html_message=plain_message)
    if sent:
        log_sent_mail(subject, plain_message, EMAIL_ADDRESS)
    else:
        log_unsent_email(subject, plain_message, EMAIL_ADDRESS)
    return sent

def flag_email(instance):
    subject = "There's been a flag on ActionRising"
    plain_message = "https://www.actionrising.com/admin/flags/flag/" + str(instance.pk)
    html_message = "<a href='https://www.actionrising.com/admin/flags/flag/" + str(instance.pk) + "/change'>Click here</a>"
    sent = send_mail(subject, plain_message, NOTIFY_EMAIL, ['actionrisingsite@gmail.com'],
        fail_silently=False, html_message=html_message)
    if sent:
        log_sent_mail(subject, plain_message, EMAIL_ADDRESS)
    else:
        log_unsent_email(subject, plain_message, EMAIL_ADDRESS)
    return sent
