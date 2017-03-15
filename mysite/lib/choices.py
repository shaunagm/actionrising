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

class StatusChoices(DjangoChoices):
    ready = ChoiceItem('ready', _('Open for action'))
    finished = ChoiceItem('finished', _('Finished'))
    withdrawn = ChoiceItem('withdrawn', _('Withdrawn'))

class ToDoStatusChoices(DjangoChoices):
    suggested = ChoiceItem('suggested', _('Suggested to you'))
    accepted = ChoiceItem('accepted', _('Accepted'))
    done = ChoiceItem('done', _('Done'))
    rejected = ChoiceItem('rejected', _('Rejected'))
    closed = ChoiceItem('closed', _('Action was closed or withdrawn'))

    @classmethod
    def third_person(cls, status):
        return {
            'suggested': 'Suggested to them',
            'accepted': 'On their to do list',
            'done': 'Action completed',
            'closed': 'Action closed before they did it',
            'rejected': 'This should never get used!'
        }[status]



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
