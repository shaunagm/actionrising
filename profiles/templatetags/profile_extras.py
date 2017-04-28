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
    viewer = context['request'].user
    actor_ok = check_privacy(action.actor.profile, viewer)
    target_ok = action.target is None or check_privacy(action.target, viewer)
    object_ok = action.action_object is None or type(action.action_object) is Comment or check_privacy(action.action_object, viewer)
    return action if actor_ok and target_ok and object_ok else None
