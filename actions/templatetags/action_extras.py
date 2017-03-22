from django import template
from mysite.lib.choices import TimeChoices

register = template.Library()

@register.assignment_tag()
def get_duration_choices():
    return [choice[1] for choice in TimeChoices.choices]
