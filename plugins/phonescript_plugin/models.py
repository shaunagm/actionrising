from __future__ import unicode_literals
from django.utils.translation import ugettext as _

import json, ast
from django.db import models
from djchoices import DjangoChoices, ChoiceItem

from actions.models import Action

# Choices

class TypeChoices(DjangoChoices):
    default = ChoiceItem('default', _('Default'))
    constituent = ChoiceItem('constituent', _('Constituent'))
    universal = ChoiceItem('universal', _('Universal'))

class PriorityChoices(DjangoChoices):
    high = ChoiceItem('3', _('High Priority'))
    medium = ChoiceItem('2', _('Medium Priority'))
    low = ChoiceItem('1', _('Low Priority'))

class RepChoices(DjangoChoices):
    senator = ChoiceItem('sen', _('Senator'))
    representative = ChoiceItem('rep', _('Representative'))
    both = ChoiceItem('both', _('Both'))

class PartyChoices(DjangoChoices):
    dem = ChoiceItem('d', _('Democrat'))
    rep = ChoiceItem('r', _('Republican'))
    all = ChoiceItem('all', _('All'))

class PositionChoices(DjangoChoices):
    for_position = ChoiceItem('for', _('For'))
    against_position = ChoiceItem('against', _('Against'))
    undecided = ChoiceItem('undecided', _('Undecided'))
    unknown = ChoiceItem('unknown', _('Position unknown'))
    all = ChoiceItem('all', _('All'))

# Note: this may belong somewhere else (misc?), since it is likely to be used by other
# plugins, but for now let's keep it here.
class Legislator(models.Model):
    '''Database of active legislators'''
    bioguide_id = models.CharField(max_length=9)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    party = models.CharField(max_length=1)
    title = models.CharField(max_length=15)
    phone = models.CharField(max_length=15)
    state = models.CharField(max_length=2, blank=True, null=True)
    district = models.CharField(max_length=10, blank=True, null=True)
    in_office = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.first_name, self.last_name)

    def short_name(self):
        return "%s %s" % (self.title, self.last_name)

    def full_appellation(self):
        return "%s %s %s (%s)" % (self.title, self.first_name, self.last_name, self.state)

    def select_name(self):
        return "%s-%s (%s)" % (self.state, self.district, self.last_name)

    def get_script_given_action(self, action):
        matches = ScriptMatcher.objects.filter(legislator=self, action=action)
        if matches and matches[0].script:
            return matches[0].script
        else:
            # Check for default scripts
            defaults = PhoneScript.objects.filter(action=action, script_type=TypeChoices.default)
            if defaults:
                return defaults[0]
        return

    def get_script_dict_given_action(self, action):
        script = self.get_script_given_action(action)
        if script:
            return {'rep': self, 'script_type': script.script_type, 'priority': int(script.priority),
                'content': script.content }
        return

class PhoneScript(models.Model):
    action = models.ForeignKey(Action)
    content = models.CharField(max_length=1000)
    script_type = models.CharField(max_length=11, choices=TypeChoices.choices,
        default=TypeChoices.default)
    # Determines when script should be shown
    always_reps = models.CharField(max_length=300, blank=True)
    priority = models.CharField(max_length=6, choices=PriorityChoices.choices,
        default=PriorityChoices.medium)
    # Conditions
    rep_type = models.CharField(max_length=7, choices=RepChoices.choices,
        default=RepChoices.both)
    party = models.CharField(max_length=10, choices=PartyChoices.choices,
        default=PartyChoices.all)
    position = models.CharField(max_length=9, choices=PositionChoices.choices,
        default=PositionChoices.all)
    committees = models.CharField(max_length=30, blank=True)
    states = models.CharField(max_length=200, blank=True)
    districts = models.CharField(max_length=300, blank=True)

    def __unicode__(self):
        if len(self.content) > 20:
            content_intro = self.content[:20]
        else:
            content_intro = self.content
        return "%s (%s for %s)" % (content_intro, self.script_type, self.action.title)

    def set_committees(self, committees):
        self.committees = json.dumps(committees)
        self.save()

    def get_committees(self):
        if self.committees:
            return json.loads(self.committees)

    def set_states(self, states):
        self.states = json.dumps(states)
        self.save()

    def get_states(self):
        if self.states:
            return json.loads(self.states)

    def set_districts(self, districts):
        self.districts = json.dumps(districts)
        self.save()

    def get_districts(self):
        if self.districts:
            return json.loads(self.districts)

    def set_always_reps(self, always_reps):
        self.always_reps = json.dumps(always_reps)
        self.save()

    def get_always_reps(self):
        if self.always_reps:
            return [int(pk) for pk in ast.literal_eval(self.always_reps)]

    def get_always_reps_as_models(self):
        return Legislator.objects.filter(pk__in=self.get_always_reps())

    def get_default_script_with_no_rep_data(self):
        if self.script_type != TypeChoices.default:
            return
        return {'rep': {'full_appellation': 'Default Script', 'phone': 'N/A'},
            'script_type': self.script_type, 'priority': int(self.priority),
            'content': self.content }

    def get_universal_scripts(self):
        if self.script_type != TypeChoices.universal:
            return
        scripts = []
        for rep in self.get_always_reps_as_models():
            scripts.append({'rep': rep, 'script_type': self.script_type,
                'priority': int(self.priority), 'content': self.content })
        return scripts

    def does_rep_meet_conditions(self, rep):
        '''Checks if the script's conditions match a given legislator'''

        # Representative type
        if self.rep_type.lower() != RepChoices.both:
            if self.rep_type.lower() != rep.title.lower():
                return False

        # Party type
        if self.party.lower() != PartyChoices.all:
            if self.party.lower() != rep.party.lower():
                return False

        # Position
        if self.position != PositionChoices.all:
            matcher = ScriptMatcher.objects.get(action=self.action, legislator=rep)
            if self.position != matcher.position:
                return False

        # Committees
        # TODO: need to do a separate query for this

        # # States
        # if self.states:
        #     if rep.state not in self.get_states():
        #         return False

        # Districts
        # TODO: what would this actually be used for?  Can ppl just pick based on
        # congressfolk (reusing always_reps?)?  Do we want a "swing district" boolean
        # option?

        return True

    def delete(self):
        # NOTE: Django bulk deletion doesn't call this, so be wary of how this model
        # gets deleted.
        scripts = ScriptMatcher.objects.filter(script=self)
        super(PhoneScript, self).delete(*args, **kwargs)
        for script in scripts:
            script.refresh_script()

class ScriptMatcher(models.Model):
    '''Creates links between action & legislator, with optional link to phonescript'''
    legislator = models.ForeignKey(Legislator)
    action = models.ForeignKey(Action)
    script = models.ForeignKey(PhoneScript, blank=True, null=True)
    position = models.CharField(max_length=9, choices=PositionChoices.choices,
        default=PositionChoices.unknown)
    notes = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        script = self.script if self.script else ""
        return "%s %s (%s)" % (self.legislator, self.action, script)

    def save(self, *args, **kwargs):
        run_update = False
        if self.pk:
            stale_item = ScriptMatcher.objects.get(pk=self.pk)
            if stale_item.position != self.position:
                run_update = True
        super(ScriptMatcher, self).save(*args, **kwargs)
        if run_update:
            self.refresh_script()

    def refresh_script(self):
        from plugins.phonescript_plugin.lib.phonescripts import get_constituent_script_for_leg
        script = get_constituent_script_for_leg(self.legislator, self.action)
        if script:
            self.script = script
        else:
            self.script = None
        self.save()
