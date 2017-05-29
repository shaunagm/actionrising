"""Store constant values that are shared across the code base.

This module stores constants which are referenced from multiple places. If
the constant is only used locally, please define it locally for clarity.

CONSTANTS

Constants are stored in the `constants_table` dictionary. The alternative
approach, storing them at the model level and using `getattr`,
risks unfortunate injection attacks.

Constant names should be descriptive and in ALL CAPS.

ACCESSING

Emails: the library `notifications/lib/email_handlers.py` handles all email
rendering using `render_to_string`. `render_to_string` has been shadowed and
the constants table injected into the context.

Templates: a context processor has been added to `mysite/settings.py` to add
constants_table's contents to all HttpRequest template renders.

In both cases, the constants can be accessed like so:
    {{ DEFAULT_ACTION_DURATION }}

Code: import constants table; if clarity matters, you can set a module level
global referencing the variable you need. E.g.,

from mysite.constants import constants_table

DEFAULT_ACTION_DURATION = constants_table['DEFAULT_ACTION_DURATION']
"""

def constants(request):
    return constants_table

constants_table = {
    'DEFAULT_ACTION_DURATION': 60,
    'DAYS_WARNING_BEFORE_CLOSURE': 3,
    'EMAIL_ADDRESS': 'actionrisingsite@gmail.com',
    'OBFUSCATED_EMAIL_ADDRESS':
        'actionrisingsite -at- gmail -dot- com',
    'SITE_URL': 'www.actionrising.com',
    'SITE_NAME': 'ActionRising',
}
