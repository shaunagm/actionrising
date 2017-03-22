from django.contrib.auth.models import User
from mysite.lib.choices import PrivacyChoices

def get_global_default_given_object(object):
    '''Finds the privacy defaults model associated with a given object'''
    if type(object) == User:
        return object.profile.privacy_defaults
    if object.get_cname() == "Profile":
        return object.privacy_defaults
    if object.get_cname() in ["Action", "Slate"]:
        return object.creator.profile.privacy_defaults
    if object.get_cname() == "ProfileActionRelationship":
        return object.profile.privacy_defaults
    if object.get_cname() == "ProfileSlateRelationship":
        return object.profile.privacy_defaults
    if object.get_cname() == "SlateActionRelationship":
        return object.slate.creator.profile.privacy_defaults

def get_global_privacy_default(object, format=None):
    '''Finds the global default privacy, in specified format, for a given object'''
    pd = get_global_default_given_object(object)
    if format == "display":
        return pd.get_global_default_display()
    if format == "decorated":
        return "Your Default (Currently '" + pd.get_global_default_display() + "')"
    return pd.global_default

def get_owner_given_object(object):
    '''Finds the owner of a given object'''
    if type(object) == User:
        return object
    if object.get_cname() == "Profile":
        return object.user
    if object.get_cname() in ["Action", "Slate"]:
        return object.creator
    if object.get_cname() == "ProfileActionRelationship":
        return object.profile.user
    if object.get_cname() == "ProfileSlateRelationship":
        return object.profile.user
    if object.get_cname() == "SlateActionRelationship":
        return object.slate.creator

def check_for_ownership(object, user):
    '''Checks whether a user is the owner of a given object'''
    object_owner = get_owner_given_object(object)
    if object_owner == user:
        return True
    return False

def get_profile_given_object(object):
    '''Gets the profile associated with a given object'''
    if type(object) == User:
        return object.profile
    if object.get_cname() == "Profile":
        return object
    if object.get_cname() in ["Slate", "Action"]:
        return object.creator.profile

def user_in_followers(object, user):
    '''Checks if user is in the followers of an object'''
    profile = get_profile_given_object(object)
    return user in profile.get_people_tracking()

def check_privacy_given_setting(privacy_setting, object, user):
    '''Checks if user passes the privacy level for a given object'''
    if privacy_setting == PrivacyChoices.public:
        return True
    if privacy_setting == PrivacyChoices.sitewide and user.is_authenticated():
        return True
    if privacy_setting == PrivacyChoices.follows and user_in_followers(object, user):
        return True
    return False

def get_privacy_setting(object):
    '''Gets relevant privacy setting for object'''
    if hasattr(object, 'privacy') and object.privacy != PrivacyChoices.inherit:
        return object.privacy
    return get_global_privacy_default(object)

def check_privacy(object, user):
    '''Checks privacy given object and user'''
    if check_for_ownership(object, user):
        return True
    if type(object) != User:
        if object.get_cname() == "ProfileActionRelationship":
            return check_privacy(object.profile.user, user) and check_privacy(object.action, user)
        if object.get_cname() == "ProfileSlateRelationship":
            return check_privacy(object.profile.user, user) and check_privacy(object.slate, user)
        if object.get_cname() == "SlateActionRelationship":
            return check_privacy(object.slate, user) and check_privacy(object.action, user)
    privacy_setting = get_privacy_setting(object)
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
