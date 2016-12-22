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
