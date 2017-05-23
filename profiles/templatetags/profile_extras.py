from django import template
from mysite.lib.privacy import check_activity
from mysite.lib.choices import ToDoStatusChoices

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_friendslist(context):
    user = context['request'].user
    if user.is_authenticated():
        return [profile.user for profile in user.profile.get_connected_people()]
    return []

@register.assignment_tag(takes_context=True)
def get_following_list(context):
    user = context['request'].user
    if user.is_authenticated():
        return [profile.user for profile in user.profile.get_people_user_follows()]
    return []

@register.simple_tag
def is_own_profile(user, object):
    return object == user

@register.assignment_tag(takes_context=True)
def filtered_feed(context, activity, own=False):
    viewer = context['request'].user
    return activity if check_activity(activity, viewer, own) else None

@register.assignment_tag(takes_context=False)
def get_status_phrase(status):
    return ToDoStatusChoices.third_person(status)
