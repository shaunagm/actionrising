from django.utils.translation import ugettext as _

PRIVACY_CHOICES = (
    ('pub', _('Visible to Public')),
    ('sit', _('Visible Sitewide')),
    # ('fol', 'Visible to Buddies and Those You Follow'),
    # ('bud', 'Visible to Buddies'),
    # ('you', 'Only Visible to You'),
    ('inh', _('Inherit')),
)

PRIVACY_DEFAULT_CHOICES = (
    ('pub', _('Visible to Public')),
    ('sit', _('Visible Sitewide')),
    # ('fol', 'Visible to Buddies and Those You Follow'),
    # ('bud', 'Visible to Buddies'),
    # ('you', 'Only Visible to You'),
)

STATUS_CHOICES = (
    # ('cre', 'In creation'),
    ('rea', _('Open for action')),
    ('fin', _('Finished')),
    ('wit', _('Withdrawn')),
)

INDIVIDUAL_STATUS_CHOICES = (
    ('sug', _('Suggested to you')),
    ('ace', _('Accepted')),
    ('don', _('Done')),
    ('wit', _('Rejected')),
)

PRIORITY_CHOICES = (
    ('low', _('Low')),
    ('med', _('Medium')),
    ('hig', _('High')),
    ('eme', _('Emergency')),
)

def check_for_ownership(object, user):
    user_profile = user.profile if hasattr(user, 'profile') else "GarbageString"
    if object in [user, user_profile]:
        return True
    if hasattr(object, 'creator'):
        if object.creator in [user, user_profile]:
            return True
    return False

def get_global_privacy_default(object, shortname=True):
    # Some of this chaining seems inefficient and absurd :(
    if object.get_cname() in "Profile":
        pd = object.privacy_defaults
    if object.get_cname() in ["Action", "Slate"]:
        pd = object.creator.profile.privacy_defaults
    if object.get_cname() in ["ProfileActionRelationship"]:
        pd = object.profile.privacy_defaults
    if object.get_cname() in ["SlateActionRelationship"]:
        pd = object.slate.creator.profile.privacy_defaults
    if shortname:
        return pd.global_default
    else:
        return pd.get_global_default_display()

def check_privacy(object, user):
    if check_for_ownership(object, user):
        return True
    if object.privacy == "inh":
        privacy_setting = get_global_privacy_default(object)
    else:
        privacy_setting = object.privacy
    if privacy_setting == "pub":
        return True
    if privacy_setting == "sit" and user.is_authenticated():
        return True
    return False

def get_global_privacy_string(obj):
    privacy = get_global_privacy_default(obj, shortname=False)
    return "Your Default (Currently '" + privacy + "')"

from functools import wraps
def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper
