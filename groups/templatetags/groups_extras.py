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