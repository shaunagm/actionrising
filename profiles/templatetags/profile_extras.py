from django import template
from django.contrib.auth.models import User
from django_comments.models import Comment
from mysite.lib.privacy import check_activity
from mysite.lib.choices import ToDoStatusChoices
from profiles.models import ProfileActionRelationship, Profile, Relationship

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

@register.assignment_tag(takes_context=True)
def filtered_feed(context, activity, own=False):
    viewer = context['request'].user
    return activity if check_activity(activity, viewer, own) else None

@register.assignment_tag(takes_context=False)
def get_status_phrase(status):
    return ToDoStatusChoices.third_person(status)
