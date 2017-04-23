from django import template

from plugins.phonescript_plugin.lib.phonescript_selects import states, districts

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_location_selects(context, override_hide=False):
    return { 'states': states, 'districts': districts }
