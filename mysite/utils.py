from django.utils.translation import ugettext as _

PRIVACY_CHOICES = (
    ('pub', _('Visible to Public')),
    ('sit', _('Visible Sitewide')),
    ('fol', _('Visible to Follows')),
    # ('you', 'Only Visible to You'),
    ('inh', _('Inherit')),
)

PRIVACY_DEFAULT_CHOICES = (
    ('pub', _('Visible to Public')),
    ('sit', _('Visible Sitewide')),
    ('fol', _('Visible to Follows')),
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

def get_follows(object):
    if object.get_cname() == "Profile":
        profile = object
    if object.get_cname() in ["Slate", "Action"]:
        profile = object.creator.profile
    return profile.get_people_tracking()

def check_privacy_given_setting(privacy_setting, object, user):
    if privacy_setting == "pub":
        return True
    if privacy_setting == "sit" and user.is_authenticated():
        return True
    if privacy_setting == "fol":
        follows = get_follows(object)
        if user in follows:
            return True
    return False

def check_privacy(object, user):
    if check_for_ownership(object, user):
        return True
    if object.get_cname() == "ProfileActionRelationship":
        return check_privacy(object.profile, user) and check_privacy(object.action, user)
    if object.get_cname() == "SlateActionRelationship":
        return check_privacy(object.slate, user) and check_privacy(object.action, user)
    privacy_setting = get_global_privacy_default(object) if object.privacy == "inh" else object.privacy
    return check_privacy_given_setting(privacy_setting, object, user)

def filter_list_for_privacy(object_list, user):
    return [obj for obj in object_list if check_privacy(obj, user)]

def filter_list_for_privacy_annotated(object_list, user):
    anonymous_count = 0
    public_list = []
    for obj in object_list:
        if check_privacy(obj, user):
            public_list.append(obj)
        else:
            anonymous_count += 1
    return {'anonymous_count': anonymous_count,
            'total_count': anonymous_count + len(public_list),
            'public_list': public_list }

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

def give_old_profiles_new_settings():
    from django.contrib.auth.models import User
    from notifications.models import NotificationSettings
    for user in User.objects.all():
        NotificationSettings.objects.create(user=user)

# Prevent bad actor from flooding us with requests, but hash it so it's not trivially easy
# to recreate TODO: set up process for periodically deleting this data (every 24 hours?)
def get_hash_given_request(request):
    import hashlib
    requester_hash = hashlib.new('DSA')
    id_string = request.META.get('HTTP_USER_AGENT', '') + request.META.get('REMOTE_ADDR')
    requester_hash.update(id_string)
    return requester_hash.hexdigest()
