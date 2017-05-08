from django.utils.translation import ugettext as _
from djchoices import DjangoChoices, ChoiceItem

class PrivacyChoices(DjangoChoices):
    public = ChoiceItem('public', _('Visible to Public')) #pub
    sitewide = ChoiceItem('sitewide', _('Visible Sitewide')) #sit
    follows = ChoiceItem('follows', _('Visible to Follows')) #fol
    inherit = ChoiceItem('inherit', _('Inherit')) #inh
    privacy_tests = {
        'public': lambda object, viewer: True,
        'sitewide': lambda object, viewer: viewer.is_authenticated(),
        'follows': lambda object, viewer: viewer.is_authenticated() and
            (object.get_creator() == viewer or object.get_profile().follows(viewer.profile))
    }

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
            'suggested': 'Suggested to',
            'accepted': 'Tracking action',
            'done': 'Completed action',
            'closed': 'Closed action',
            'rejected': 'Rejected action'
        }[status]

class PriorityChoices(DjangoChoices):
    low = ChoiceItem('low', _('Low'))
    medium = ChoiceItem('medium', _('Medium'))
    high = ChoiceItem('high', _('High'))
    emergency = ChoiceItem('emergency', _('Emergency'))

class TimeChoices(DjangoChoices):
    minutes = ChoiceItem('minutes', _('Ten minutes or less')) #A
    hour = ChoiceItem('hour', _('Under an hour')) #B
    hours = ChoiceItem('hours', _('A few hours')) #C
    day = ChoiceItem('day', _('A day or more, not ongoing')) #E
    minor = ChoiceItem('minor', _('Minor ongoing commitment')) #F
    major = ChoiceItem('major', _('Major ongoing commitment')) #G
    unknown = ChoiceItem('unknown', _('Unknown or variable')) #H

class DailyActionSourceChoices(DjangoChoices):
    many = ChoiceItem('many', _('A lot'))
    few = ChoiceItem('few', _('A little'))
    none = ChoiceItem('none', _('None'))

class CommitmentStatusChoices(DjangoChoices):
    waiting = ChoiceItem('waiting', _('Commitment made, not yet at deadline'))
    active = ChoiceItem('active', _('Commitment made, past deadline'))
    completed = ChoiceItem('completed', _('Commitment carried out'))
    expired = ChoiceItem('expired', _('Commitment expired, user took too long'))
    removed = ChoiceItem('removed', _('Par was closed or deleted'))
