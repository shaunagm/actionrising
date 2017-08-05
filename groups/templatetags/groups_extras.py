from django import template
from mysite.lib.privacy import check_privacy

register = template.Library()

@register.assignment_tag(takes_context=True)
def can_access(context, object):
    viewer = context['request'].user
    return check_privacy(object, viewer)

@register.assignment_tag(takes_context=True)
def is_member(context, object):
    viewer = context['request'].user
    return object.hasMember(viewer)

@register.assignment_tag(takes_context=True)
def is_admin(context, object):
    viewer = context['request'].user
    return object.hasAdmin(viewer)

@register.assignment_tag(takes_context=True)
def profile_is_admin(context, user):
    group = context['object']
    return group.hasAdmin(user)

@register.assignment_tag(takes_context=True)
def get_user_role(context, user):
    group = context['object']
    if user == group.owner:
        return "owner"
    if group.hasAdmin(user):
        return "admin"
    return "member"


