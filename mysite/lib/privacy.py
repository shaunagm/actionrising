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
