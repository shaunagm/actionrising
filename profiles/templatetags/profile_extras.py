from django import template
from django.contrib.auth.models import User
from django_comments.models import Comment
from mysite.lib.privacy import check_privacy
from profiles.models import ProfileActionRelationship, Profile, Relationship

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_friendslist(context):
    user = context['request'].user
    if user.is_authenticated():
        return [profile.user for profile in user.profile.get_connected_people()]
    return []

@register.assignment_tag(takes_context=True)
def filtered_feed(context, action):
    user = context['request'].user
    if not check_privacy(action.actor.profile, user):
        return []
    if action.target is not None:
        target = action.target.profile if type(action.target) == User else action.target
        if not check_privacy(target, user):
            return []
    if type(action.action_object) is not Comment and action.action_object is not None and not check_privacy(action.action_object, user):
        return []
    return action

@register.assignment_tag(takes_context=True)
def others_filtered_feed(context, action):
    if filtered_feed(context, action):
        user = context['request'].user
        names = [item.username for item in [action.actor, action.target, action.action_object] if type(item) == User]
        if user.username not in names:
            return action
        else:
            return []
    else:
        return []

@register.simple_tag
def is_own_profile(user, object):
    return object.username == user.username
