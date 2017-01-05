from django import template
from django.contrib.auth.models import User
from django_comments.models import Comment
from mysite.lib.choices import INDIVIDUAL_STATUS_CHOICES
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
        if type(action.target) == User:
            if not check_privacy(action.target.profile, user):
                return []
        else:
            if not check_privacy(action.target, user):
                return []
    if type(action.action_object) is not Comment and action.action_object is not None and not check_privacy(action.action_object, user):
        return []
    return action
