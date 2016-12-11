from django import template
from django.contrib.auth.models import User
from mysite.utils import INDIVIDUAL_STATUS_CHOICES, check_privacy
from profiles.models import ProfileActionRelationship, Profile, Relationship

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_friendslist(context):
    user = context['request'].user
    if user.is_authenticated():
        return [profile.user for profile in user.profile.get_connected_people()]
    return []

@register.assignment_tag(takes_context=True)
def get_relationship(context, target_user):
    current_profile = context['request'].user.profile
    relationship = current_profile.get_relationship_given_profile(target_user.profile)
    # defaults
    info = {'is_following': False, 'follow_statement': "Follow this user",
        'account_statement': 'Make this user an accountability buddy', 'mute_statement': 'Mute this user'}
    if not relationship:
        return info
    if relationship.current_profile_follows_target(current_profile):
        info['is_following'] = True
        info['follow_statement'] = "Unfollow this user"
    if relationship.current_profile_accountable_to_target(current_profile):
        info['account_statement'] = "Remove user as accountability buddy"
    if relationship.current_profile_mutes_target(current_profile):
        info['mute_statement'] = "Unmute this user"
    return info

@register.assignment_tag(takes_context=True)
def get_action_status(context, public_list):
    action=context['action']
    action_status = {}

    for status in INDIVIDUAL_STATUS_CHOICES:
        action_status[status[0]] = []

    all_pars = ProfileActionRelationship.objects.filter(
            action=action
        ).filter(profile__in=public_list)

    for par in all_pars:
        action_status[par.status].append(par)

    return action_status

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
    if action.action_object is not None and not check_privacy(action.action_object, user):
        return []
    return action
