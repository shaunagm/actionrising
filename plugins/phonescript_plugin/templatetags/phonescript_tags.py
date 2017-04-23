from django import template
from django.core.cache import cache

from plugins.phonescript_plugin.lib.phonescript_selects import states

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_location_selects(context, override_hide=False):
    districts = cache.get('district_selects')
    return { 'states': states, 'districts': districts }
