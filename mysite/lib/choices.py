from django.utils.translation import ugettext as _

PRIVACY_CHOICES = (
    ('pub', _('Visible to Public')),
    ('sit', _('Visible Sitewide')),
    ('fol', _('Visible to Follows')),
    # ('you', 'Only Visible to You'),
    ('inh', _('Inherit')),
)

PRIVACY_DEFAULT_CHOICES = (
    ('pub', _('Visible to Public')),
    ('sit', _('Visible Sitewide')),
    ('fol', _('Visible to Follows')),
    # ('fol', 'Visible to Buddies and Those You Follow'),
    # ('bud', 'Visible to Buddies'),
    # ('you', 'Only Visible to You'),
)

STATUS_CHOICES = (
    # ('cre', 'In creation'),
    ('rea', _('Open for action')),
    ('fin', _('Finished')),
    ('wit', _('Withdrawn')),
)

INDIVIDUAL_STATUS_CHOICES = (
    ('sug', _('Suggested to you')),
    ('ace', _('Accepted')),
    ('don', _('Done')),
    ('wit', _('Rejected')),
)

PRIORITY_CHOICES = (
    ('low', _('Low')),
    ('med', _('Medium')),
    ('hig', _('High')),
    ('eme', _('Emergency')),
)

TIME_CHOICES = (
    ('A', _('Ten minutes or less')),
    ('B', _('Under an hour')),
    ('C', _('A few hours')),
    ('E', _('A day or more, not ongoing')),
    ('F', _('Minor ongoing commitment')),
    ('G', _('Major ongoing commitment')),
    ('H', _('Unknown or variable')),
)
