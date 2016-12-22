from django import template
from mysite.lib.choices import TIME_CHOICES

register = template.Library()

@register.assignment_tag()
def get_duration_choices():
    return [choice[1] for choice in TIME_CHOICES]
