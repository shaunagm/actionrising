from django import template
from mysite.lib.privacy import check_privacy

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_can_edit(context, object):
    viewer = context['request'].user
    if viewer == object.creator:
        return True
    return viewer.has_perm('administer_slate', object)