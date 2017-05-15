"""Store constant values that are shared across the code base.

This module stores constants which are referenced from multiple places. If
the constant is only used locally, please define it locally for clarity.


CONSTANTS

Constants are stored in the `constants_table` dictionary. The alternative
approach, `getattr`, risks unfortunate injection attacks.

Constant names should be descriptive and in ALL CAPS.


TEMPLATE TAGS FOR ACCESSING CONSTANTS

The `constants` template tag is used to access constants from templates. To
support this tag, it must be installed as part of `settings.py` in every app.
The tag is accessed from templates like so:

    {% constants 'ACTION_DEADLINE' %}


Todo:
	* Migrate the constants!
"""

from django import template

register = template.Library()


@register.simple_tag
def constants(constant_name):
    return constants_table[constant_name]

constants_table = {
    'ACTION_DEFAULT_CLOSE_DEADLINE': 50
}