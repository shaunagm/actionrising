PRIVACY_CHOICES = (
    ('pub', 'Visible to Public'),
    ('sit', 'Visible Sitewide'),
    # ('fol', 'Visible to Buddies and Those You Follow'),
    # ('bud', 'Visible to Buddies'),
    # ('you', 'Only Visible to You'),
    # ('inh', 'Inherit'),
)

STATUS_CHOICES = (
    ('cre', 'In creation'),
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

def check_profile_privacy(object, user):
    privacy_setting = object.privacy if object.privacy != "inh" else object.privacy_defaults.global_default
    if privacy_setting == "pub":
        return True
    if privacy_setting == "sit" and user.is_authenticated():
        return True
    return False

def check_privacy(object, user):
    if object.get_cname() == "Profile":
        return check_profile_privacy(object, user)
    return False
