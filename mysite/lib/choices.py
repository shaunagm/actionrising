from django.utils.translation import ugettext as _
from djchoices import DjangoChoices, ChoiceItem

class PrivacyChoices(DjangoChoices):
    public = ChoiceItem('public', _('Visible to Public')) #pub
    sitewide = ChoiceItem('sitewide', _('Visible Sitewide')) #sit
    follows = ChoiceItem('follows', _('Visible to Follows')) #fol
    inherit = ChoiceItem('inherit', _('Inherit')) #inh

    @classmethod
    def default_choices(cls):
        return cls.choices[:-1]

    @classmethod
    def personalized(cls, user_choice):
        return cls.choices[:-1] + (('inherit', user_choice),)

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
    ('clo', _('Action was closed or withdrawn')),
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

DAILY_ACTION_SOURCE_CHOICES = (
    ('many', _('A lot')),
    ('few', _('A little')),
    ('none', _('None')),
)

COMMITMENT_STATUS_CHOICES = (
    ('waiting', _('Commitment made, not yet at deadline')),
    ('active', _('Commitment made, past deadline')),
    ('completed', _('Commitment carried out')),
    ('expired', _('Commitment expired, user took too long')),
    ('removed', _('Par was closed or deleted')),
)
