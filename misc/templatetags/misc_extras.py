import random
from django import template
from django.template.loader import select_template
from plugins.site_plugin_conf import plugins

register = template.Library()

quote_list = ["'How wonderful it is that nobody need wait a single moment before starting to improve the world.' - Anne Frank"]

@register.simple_tag()
def get_footer_quote():
    return random.choice(quote_list)
