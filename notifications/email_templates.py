def add_footer(email_message, html_message, profile):
    plain_footer = "\n\nTo edit your notification settings, go to 'Your Profile' on www.actionrising.com."
    html_footer = "<br /><br /><a href='%s'>Change your notification settings</a>." % profile.get_edit_url_with_domain()
    return email_message + plain_footer, html_message + html_footer

# Follow email templates
FOLLOW_SUBJ = "%s is now following you on ActionRising"
FOLLOW_PLAIN_MUTUAL = "%s is following you on ActionRising. You now follow each other!"
FOLLOW_HTML_MUTUAL = "<a href='%s'>%s</a> is following you on ActionRising. You now follow each other!"
FOLLOW_PLAIN_NEW = "%sis following you on ActionRising. You don't follow them, so consider following them back!"
FOLLOW_HTML_NEW = "<a href='%s'>%s</a> is following you on ActionRising. You don't follow them, so consider following them back!"

def generate_follow_email(follower, target):
    relationship = target.get_relationship_given_profile(follower)
    email_subject = FOLLOW_SUBJ % follower.get_name()
    if relationship.current_profile_follows_target(target):
        email_message = FOLLOW_PLAIN_MUTUAL % follower.get_name()
        html_message = FOLLOW_HTML_MUTUAL % (follower.get_absolute_url_with_domain(),
            follower.get_name())
    else:
        email_message = FOLLOW_PLAIN_NEW % follower.get_name()
        html_message = FOLLOW_HTML_NEW % (follower.get_absolute_url_with_domain(),
            follower.get_name())
    email_message, html_message = add_footer(email_message, html_message, target)
    return email_subject, email_message, html_message

# Someone "taking" your action templates
TAKE_ACTION_SUBJ = "%s is taking one of your actions on ActionRising"
TAKE_ACTION_PLAIN = "%s is taking your action, %s.  Your action now has %s."
TAKE_ACTION_HTML = "<a href='%s'>%s</a> is taking your action, <a href='%s'>%s</a>.  " \
    "Your action now has %s."

def generate_take_action_email(creator, instance):
    from mysite.utils import filter_list_for_privacy_annotated
    actor = instance.actor.profile
    action = instance.target
    trackers = filter_list_for_privacy_annotated(action.profileactionrelationship_set.all(), actor.user)
    trackers = trackers['total_count']
    tracker_string = "%s people tracking it" % trackers if trackers > 1 else "%s person tracking it" % trackers
    email_subject = TAKE_ACTION_SUBJ % actor.get_name()
    email_message = TAKE_ACTION_PLAIN % (actor.get_name(), action, tracker_string)
    html_message = TAKE_ACTION_HTML % (actor.get_absolute_url_with_domain(),
        actor.get_name(), action.get_absolute_url_with_domain(), action, tracker_string)
    email_message, html_message = add_footer(email_message, html_message, creator)
    return email_subject, email_message, html_message

# Add action to slate templates
ADD_SLATE_SUBJ = "%s added your action to a slate on ActionRising"
ADD_SLATE_PLAIN = "%s added your action %s to the slate %s.  Your action is now part of %s."
ADD_SLATE_HTML = "<a href='%s'>%s</a> added your action <a href='%s'>%s</a> to the slate " \
    "<a href='%s'>%s</a>.  Your action is now part of %s."

def generate_add_to_slate_email(creator, instance):
    adder = instance.actor.profile
    action = instance.action_object
    slate = instance.target
    linked_slates = action.slate_set.count()
    slate_string = "%s slates" % linked_slates if linked_slates > 1 else "%s slate" % linked_slates
    email_subject = ADD_SLATE_SUBJ % adder.get_name()
    email_message = ADD_SLATE_PLAIN % (adder.get_name(), action, slate, slate_string)
    html_message = ADD_SLATE_HTML % (adder.get_absolute_url_with_domain(),
        adder.get_name(), action.get_absolute_url_with_domain(), action,
        slate.get_absolute_url_with_domain(), slate, slate_string)
    email_message, html_message = add_footer(email_message, html_message, creator)
    return email_subject, email_message, html_message


# Comment templates
COMMENT_SUBJ = "%s commented on your action on ActionRising"
COMMENT_PLAIN = "%s commented on your action %s."
COMMENT_HTML = "<a href='%s'>%s</a> commented on your action <a href='%s'>%s</a>."

def generate_comment_email(instance):
    commenter = instance.actor.profile
    action = instance.target
    email_subject = COMMENT_SUBJ % commenter.get_name()
    email_message = COMMENT_PLAIN % (commenter.get_name(), action)
    html_message = COMMENT_HTML % (commenter.get_absolute_url_with_domain(),
        commenter.get_name(), action.get_absolute_url_with_domain(), action)
    email_message, html_message = add_footer(email_message, html_message, action.creator.profile)
    return email_subject, email_message, html_message

# Daily action template
DAILY_SUBJ = "Your Daily Action from ActionRising"
DAILY_YOURS_PLAIN = "Your action for today comes from your personal list of actions:\n\n" \
    "%s\n\nReady to take action?"
DAILY_YOURS_HTML = "Your action for today comes from your personal list of actions:<br /><br />" \
    "<a href='%s'>%s</a><br /><br />Ready to take action?"
DAILY_TOP_PLAIN = "Your action for today comes from the most popular actions on the site:\n\n" \
    "%s\n\nReady to take action?"
DAILY_TOP_HTML = "Your action for today comes from the most popular actions on the site:<br /><br />" \
    "<a href='%s'>%s</a><br /><br />Ready to take action?"

def generate_daily_action_email(action, kind, profile):
    if kind == "yours":
        email_message = DAILY_YOURS_PLAIN % action
        html_message = DAILY_YOURS_HTML % (action.get_absolute_url_with_domain(), action)
    else:
        email_message = DAILY_TOP_PLAIN % action
        html_message = DAILY_TOP_HTML % (action.get_absolute_url_with_domain(), action)
    email_message, html_message = add_footer(email_message, html_message, profile)
    return DAILY_SUBJ, email_message, html_message

# Invite notification template

INVITE_SUBJ = "You've been invited to join ActionRising"
INVITE_BLURB = "ActionRising is a platform created to help individuals and communities figure out their next steps. We want you to take action - specific, meaningful, positive action - that fits the time and energy you have available.
INVITE_PLAIN = "You have been invited to join ActionRising by %s. They say:\n\n%s\n\n" \
    + INVITE_BLURB + "\n\nTo get started, visit %s"
INVITE_HTML = "You have been invited to join ActionRising by %s. They say:<br /><br />%s<br /><br />" \
    + INVITE_BLURB + "<br /><br /><a href='%s'>Click here</a> to get started."

REQUEST_SUBJ = "Your request to join ActionRising has been approved"
REQUEST_PLAIN = "Your request to join ActionRising has been approved. To get started, visit %s"
REQUEST_HTML = "Your request to join ActionRising has been approved. <a href='%s'>Click here</a> " \
    + "to get started."

def generate_invite_notification_email(kind, invite):
    if kind == "self":
        email_subj = REQUEST_SUBJ
        email_message = REQUEST_PLAIN % invite.get_confirmation_url()
        html_message = REQUEST_HTML % invite.get_confirmation_url()
    elif kind == "invited":
        email_subj = INVITE_SUBJ
        email_message = INVITE_PLAIN % (invite.get_inviter_string(), invite.message,
            invite.get_confirmation_url())
        html_message = INVITE_HTML % (invite.get_inviter_string(), invite.message,
            invite.get_confirmation_url())
    return email_subj, email_message, html_message

# Suggestion template

SUGGESTION_SUBJ = "%s suggested an action for you on ActionRising"
SUGGESTION_PLAIN = "%s suggested action %s for you.  Accept or reject suggested actions here: %s"
SUGGESTION_HTML = "<a href='%s'>%s</a> suggested action <a href='%s'>%s</a> to you.  You can " \
    + "accept or reject suggested actions <a href='%s'>here</a>."

def generate_suggestion_email(instance, target_user):
    suggester = instance.actor
    email_subj = SUGGESTION_SUBJ % suggester.username
    email_message = SUGGESTION_PLAIN % (suggester.username, instance.action_object.title,
        target_user.get_suggestion_url_with_domain())
    html_message = SUGGESTION_HTML % (suggester.profile.get_absolute_url_with_domain(),
        suggester.username, instance.action_object.get_absolute_url_with_domain(),
        instance.action_object.title, target_user.get_suggestion_url_with_domain())
    email_message, html_message = add_footer(email_message, html_message, instance.target.profile)
    return email_subj, email_message, html_message
