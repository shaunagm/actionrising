from django.contrib.auth.models import User
from choices import PrivacyChoices

def get_global_privacy_default(object, format=None):
    '''Finds the global default privacy, in specified format, for a given object'''
    pd = object.profile.privacy_defaults if type(object) == User else object.get_profile().privacy_defaults
    if format == "display":
        return pd.get_global_default_display()
    if format == "decorated":
        return "Your Default (Currently '" + pd.get_global_default_display() + "')"
    return pd.global_default

def check_privacy(object, viewer):
    '''Returns True if viewer is allowed to see object, else False.'''
    viewable = object.profile if type(object) is User else object
    return viewable.is_visible_to(viewer)

def filter_list_for_privacy(object_list, user):
    return [obj for obj in object_list if check_privacy(obj, user)]

def filter_list_for_privacy_annotated(object_list, user):
    public_list = [obj for obj in object_list if check_privacy(obj, user)]
    anonymous_count = len(object_list) - len(public_list)
    return {'anonymous_count': anonymous_count,
            'total_count': len(object_list),
            'public_list': public_list }

def filtered_list_view(model, user):
    '''
    model: a model like Profile, Action, or Slate
    user: the current authenticated user
    returns: [object]
    Gets the objects of model that user is allowed to see.'''
    if user.is_authenticated():
        objects = model.objects.all()
        follows_user = [profile.get_creator() for profile in user.profile.get_followers()]
        visible = [object for object in objects
                   if object.current_privacy in [PrivacyChoices.public, PrivacyChoices.sitewide]
                   or (object.get_creator() is user or object.get_creator() in follows_user)]
        return model.default_sort(visible)
    else:
        return list(model.objects.filter(current_privacy=PrivacyChoices.public).order_by(model.default_order_field()))
