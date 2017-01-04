from django import template

from commitments.models import Commitment

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_commitment(context):
    user = context['request'].user
    action = context['action']
    c = Commitment.objects.filter(profile=user.profile, action=action)
    if c:
        c = c[0]
        if c.status in ['waiting', 'active']:
            return c
        else:
            return "Closed"
    return None
