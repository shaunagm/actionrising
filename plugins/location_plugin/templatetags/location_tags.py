from django import template

from django.contrib.contenttypes.models import ContentType
from plugins.location_plugin.models import Location
from plugins.location_plugin.lib.location_selects import states, districts

register = template.Library()

def get_location_helper(located_object):
    if located_object.__class__.__name__ == "AnonymousUser":
        return
    if located_object.__class__.__name__ == "User":
        located_object = located_object.profile
    ctype = ContentType.objects.get_for_model(located_object)
    return Location.objects.filter(content_type=ctype, object_id=located_object.pk).first()

@register.assignment_tag(takes_context=True)
def get_location(context, located_object, override_hide=False):
    location = get_location_helper(located_object)
    if location and (not location.hide_location or override_hide):
        return location.location

@register.assignment_tag(takes_context=True)
def get_state_and_district(context, located_object, override_hide=False):
    location = get_location_helper(located_object)
    if location and (not location.hide_location or override_hide):
        return {'state': location.state, 'district': location.district}

@register.assignment_tag(takes_context=True)
def get_location_selects(context, override_hide=False):
    return { 'states': states, 'districts': districts }
