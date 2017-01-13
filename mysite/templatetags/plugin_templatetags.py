from django import template
from django.template.loader import select_template
from plugins.site_plugin_conf import plugins, plugin_template_options

register = template.Library()

@register.simple_tag(takes_context=True)
def get_plugin_templates(context, called_by):
    templates_list = []
    for plugin in plugins:
        if plugin['enabled']:
            template_str = plugin['name'] + plugin_template_options[called_by]
            templates_list.append(template_str)
    valid_template = select_template(templates_list)
    return valid_template.render(context)

# Usage
#
# Needs to feed in the specifics (action list include, etc)
#
# {% get_plugin_template as valid_template %}
