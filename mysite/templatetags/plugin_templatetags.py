from django import template
from django.template.loader import select_template
from plugins.site_plugin_conf import field_plugins

register = template.Library()

@register.simple_tag(takes_context=True)
def get_plugin_templates(context, called_by):
    templates_list = []
    for plugin in field_plugins:
        if plugin['enabled']:
            template_str = plugin['conf_dict'].get_template(called_by)
            templates_list.append(template_str)
    valid_template = select_template(templates_list)
    return valid_template.render(context)
