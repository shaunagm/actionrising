from django import template

from plugins.location_plugin.models import Location

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_location(context, located_object):
    return Location.objects.filter(content_object=located_object)
