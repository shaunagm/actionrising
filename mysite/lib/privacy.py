from django.contrib.auth.models import User, AnonymousUser
from choices import PrivacyChoices
from django_comments.models import Comment

#########################################################
# Objects call these tests from their is_visible methods
#########################################################

def public_test(object, user, follows_user = None):
    '''Takes extra arguments so it can be used indiscriminately,
    but just returns True because public objects are visible to everyone.'''
    return True

def sitewide_test(object, user, follows_user = None):
    '''Takes an extra argument for conformity, but just tests
    whether user can see sitewide object, ie, is logged in.'''
    return user.is_authenticated()

def follows_test(object, user, follows_user = None):
    '''
    object: object with privacy setting
    user: User trying to view object
    follows_user: optional list of Profiles that follow user - providing
        it increases efficiency when processing a list of objects
    Returns Boolean - whether user can view object
    Does not take action anonymity into account.'''
    creator = object.get_creator()
    return creator == user or creator.profile in get_follows(user, follows_user)

# maps privacy settings to functions that can be applied to test them
privacy_tests = {
    'public': public_test,
    'sitewide': sitewide_test,
    'follows': follows_test
}

##########################################################
# Helpers
##########################################################

def get_follows(user, follows_user = None):
    '''
    user: User trying to view objects
    follows_user: optional list of Profiles that follow user, provided for efficiency
    Returns [Profile]
    Returns the list follows_user without doing extra calculations if it's present. Otherwise,
    gets the list while handling the possibility that user is not logged in.'''
    if follows_user:
        return follows_user
    else:
        return user.profile.get_followers() if user.is_authenticated() else []

def check_anonymity(object, include_anonymous):
    '''
    object: object such as an Action, Profile, etc
    include_anonymous: Boolean
    Returns Boolean - whether this object should be shown based on its anonymity.'''
    return include_anonymous or not(hasattr(object, 'named')) or object.named()

##########################################################
# "Exported" privacy functions
##########################################################

def get_global_privacy_default(object, format=None):
    '''Finds the global default privacy, in specified format, for a given object'''
    pd = object.profile.privacy_defaults if type(object) == User else object.get_profile().privacy_defaults
    if format == "display":
        return pd.get_global_default_display()
    if format == "decorated":
        return "Your Default (Currently '" + pd.get_global_default_display() + "')"
    return pd.global_default

def check_privacy(object, viewer, follows_user = None):
    '''Returns True if viewer is allowed to see object, else False.'''
    if isinstance(object, Comment):
        return True
    viewable = object.profile if isinstance(object, User) else object
    return viewable.is_visible_to(viewer, follows_user)

def apply_check_privacy(objects, user, include_anonymous = True):
    '''Efficiently applies check_privacy to a list of objects.'''
    follows_user = get_follows(user)
    return [object for object in objects if
            check_privacy(object, user, follows_user) and
            check_anonymity(object, include_anonymous)]

def check_activity(activity, viewer, own):
    '''
    activity: item from activity stream; has actor, maybe target, maybe action_object
    viewer: User logged in
    own: boolean - should be True when the activity feed is of your own activity; determines
        whether you should see activity involving anonymized actions.
    Returns boolean - whether viewer should see this activity based on privacy and anonymity'''
    accessible = lambda object: check_privacy(object, viewer) and check_anonymity(object, own)
    actor_ok = accessible(activity.actor)
    target_ok = activity.target is None or accessible(activity.target)
    object_ok = activity.action_object is None or \
        isinstance(activity.action_object, Comment) or \
        accessible(activity.action_object)
    return actor_ok and target_ok and object_ok

def filter_list_for_privacy_annotated(object_list, user, include_anonymous = False):
    '''
    object_list: list of objects like Actions, Slates, etc
    user: User viewing objects
    include_anonymous: Boolean that determines whether anonymized actions are shown
    returns dict:
        restricted_count: number of objects user can't see
        total_count: total number of objects
        visible_list: list of objects user can see'''
    visible_list = apply_check_privacy(object_list, user, include_anonymous)
    return {'restricted_count': len(object_list) - len(visible_list),
            'total_count': len(object_list),
            'visible_list': visible_list }
