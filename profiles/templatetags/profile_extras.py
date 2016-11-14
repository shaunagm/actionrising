from django import template
from profiles.models import Profile

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_friendslist(context):
    user=context['request'].user
    return [profile.user for profile in user.profile.connections.all()]
