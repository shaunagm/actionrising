from django.contrib.auth.models import User

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
