PRIVACY_CHOICES = (
    ('pub', 'Visible to Public'),
    ('sit', 'Visible Sitewide'),
    # ('fol', 'Visible to Buddies and Those You Follow'),
    # ('bud', 'Visible to Buddies'),
    # ('you', 'Only Visible to You'),
    ('inh', 'Inherit'),
)

PRIVACY_DEFAULT_CHOICES = (
    ('pub', 'Visible to Public'),
    ('sit', 'Visible Sitewide'),
    # ('fol', 'Visible to Buddies and Those You Follow'),
    # ('bud', 'Visible to Buddies'),
    # ('you', 'Only Visible to You'),
)

STATUS_CHOICES = (
    # ('cre', 'In creation'),
    ('rea', 'Open for action'),
    ('fin', 'Finished'),
    ('wit', 'Withdrawn'),
)

INDIVIDUAL_STATUS_CHOICES = (
    ('sug', 'Suggested to you'),
    ('ace', 'Accepted'),
    ('don', 'Done'),
    ('wit', 'Rejected'),
)

PRIORITY_CHOICES = (
    ('low', 'Low'),
    ('med', 'Medium'),
    ('hig', 'High'),
    ('eme', 'Emergency'),
)

def check_for_ownership(object, user):
    user_profile = user.profile if hasattr(user, 'profile') else "GarbageString"
    if object in [user, user_profile]:
        return True
    if hasattr(object, 'creator'):
        if object.creator in [user, user_profile]:
            return True
    return False

def get_global_privacy_default(object):
    # Some of this chaining seems inefficient and absurd :(
    if object.get_cname() in "Profile":
        return object.privacy_defaults.global_default
    if object.get_cname() in ["Action", "Slate"]:
        return object.creator.profile.privacy_defaults.global_default
    if object.get_cname() in "ProfileActionRelationship":
        return object.profile.privacy_defaults.global_default
    if object.get_cname() in "SlateActionRelationship":
        return object.slate.creator.profile.privacy_defaults.global_default

def check_privacy(object, user):
    if check_for_ownership(object, user):
        return True
    if object.privacy == "inh":
        privacy_setting = get_global_privacy_default(object)
    else:
        privacy_setting = object.privacy
    if privacy_setting == "pub":
        return True
    if privacy_setting == "sit" and user.is_authenticated():
        return True
    return False
