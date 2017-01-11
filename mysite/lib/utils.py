#################
### Logistics ###
#################

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

# Hash it so it's not trivially easy to recreate
# TODO: set up process for periodically deleting this data (every 24 hours?)
def get_hash_given_request(request):
    """
    Prevent bad actor from flooding us with requests
    """
    import hashlib
    requester_hash = hashlib.new('DSA')
    id_string = request.META.get('HTTP_USER_AGENT', '') + request.META.get('REMOTE_ADDR')
    requester_hash.update(id_string)
    return requester_hash.hexdigest()

#####################
### DB management ###
#####################

def give_old_profiles_new_settings():
    from django.contrib.auth.models import User
    from notifications.models import NotificationSettings
    for user in User.objects.all():
        NotificationSettings.objects.create(user=user)

########################
### Model name logic ###
########################

from django.contrib.contenttypes.models import ContentType
def get_content_object(model, pk):
    '''Returns a content object given model name as string and pk'''
    if model.lower() in ["action", "slate"]:
        app_label = "actions"
    else:
        app_label = "profiles"
    ct = ContentType.objects.get(app_label=app_label, model=model.lower())
    return ct.get_object_for_this_type(pk=pk)

##############
### Slugs! ###
##############
from django.core.validators import RegexValidator
from django.template.defaultfilters import slugify

slug_validator = [
    RegexValidator(
        regex=re.compile(r"^[a-z0-9-]+$"),
        message="Enter a slug, using only lowercase letters, numbers, and dashes.",
        code="invalid"
    )
]

def slugify_helper(object_model, slug):
    counter = 0
    temp_slug = slugify(slug)[:45]
    while True:
        if object_model.objects.filter(slug=temp_slug):
            temp_slug += str(counter)
            counter += 1
            continue
        break
    return temp_slug
