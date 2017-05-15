import random
from bleach import clean
from django import template
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

register = template.Library()

quote_list = ["'How wonderful it is that nobody need wait a single moment before starting to improve the world.' - Anne Frank"]


@register.simple_tag()
def get_footer_quote():
    return random.choice(quote_list)


@register.filter
@stringfilter
def bleach(value):
    if isinstance(value, SafeData):
        return value
    else:
        return mark_safe(clean(value))
