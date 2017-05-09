from django.contrib.auth.models import User
from choices import PrivacyChoices
from django_comments.models import Comment

privacy_tests = {
    'public': lambda object, viewer: True,
    'sitewide': lambda object, viewer: viewer.is_authenticated(),
    'follows': lambda object, viewer: viewer.is_authenticated() and
        (object.get_creator() == viewer or object.get_profile().follows(viewer.profile))
}

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
    if isinstance(object, Comment):
        return object
    viewable = object.profile if type(object) is User else object
    return viewable.is_visible_to(viewer)

def filter_list_for_privacy_annotated(object_list, user, include_anonymous = False):
    visible_list = [obj for obj in object_list
                    if check_privacy(obj, user) and (include_anonymous or obj.named())]
    return {'restricted_count': len(object_list) - len(visible_list),
            'total_count': len(object_list),
            'visible_list': visible_list }

def filtered_list_view(model, user):
    '''
    model: a model like Profile, Action, or Slate
    user: the current authenticated user
    returns: [object]
    Gets the objects of model that user is allowed to see.
    More efficient than looping with check_privacy.'''
    if user.is_authenticated():
        objects = model.objects.all()
        follows_user = [profile.get_creator() for profile in user.profile.get_followers()]
        visible = [object for object in objects
                   if object.current_privacy in [PrivacyChoices.public, PrivacyChoices.sitewide]
                   or (object.get_creator() == user or (object.named() and object.get_creator() in follows_user))]
        return model.default_sort(visible)
    else:
        return list(model.objects.filter(current_privacy=PrivacyChoices.public).order_by(model.default_order_field()))

def check_activity(activity, viewer, own):
    # checks for privacy permissions and only shows your anonymous activity to you
    accessible = lambda object: check_privacy(object, viewer) and (own or isinstance(object, User) or object.named())
    actor_ok = accessible(activity.actor)
    target_ok = activity.target is None or accessible(activity.target)
    object_ok = activity.action_object is None or type(activity.action_object) is Comment or accessible(activity.action_object)
    return actor_ok and target_ok and object_ok
