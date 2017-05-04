from django.contrib.auth.models import User
from django.db.models import Q
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
    Gets the objects of model that user is allowed to see'''
    if user.is_authenticated():
        unconditional = model.objects.filter(privacy__in=[PrivacyChoices.public, PrivacyChoices.sitewide])
        followed = [profile.pk for profile in user.profile.get_people_user_follows()]
        visible_followed = [object for object in model.objects.filter(privacy=PrivacyChoices.follows)
                                   if object.get_creator() is user or object.get_creator() in followed]
        return model.default_sort(list(unconditional) + visible_followed)
    else:
        return list(model.objects.filter(privacy=PrivacyChoices.public).order_by(model.default_order_field()))
