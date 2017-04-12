from __future__ import unicode_literals

import json, ast
from django.db import models

from actions.models import Action

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

    def __unicode__(self):
        return "%s %s %s" % (self.title, self.first_name, self.last_name)

    def short_name(self):
        return "%s %s" % (self.title, self.last_name)

    def full_appellation(self):
        return "%s %s %s (%s)" % (self.title, self.first_name, self.last_name, self.state)

    def get_script_given_action(self, action):
        matches = ScriptMatcher.objects.filter(legislator=self, action=action)
        if matches and matches[0].script:
            return matches[0].script
        else:
            # Check for default scripts
            defaults = PhoneScript.objects.filter(action=action, script_type="default")
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
    TYPE_CHOICES = [
        ('default', 'Default'),
        ('constituent', 'Constituent'),
        ('universal', 'Universal'),
    ]
    script_type = models.CharField(max_length=11, choices=TYPE_CHOICES, default="none")
    # Determines when script should be shown
    always_reps = models.CharField(max_length=300, blank=True)
    PRIORITY_CHOICES = [
        ('3', 'High Priority'),
        ('2', 'Medium Priority'),
        ('1', 'Low Priority'),
    ]
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default="2")
    # Conditions
    REP_CHOICES = [
        ('sen', 'Senator'),
        ('rep', 'Representative'),
        ('both', 'Both'),
    ]
    rep_type = models.CharField(max_length=7, choices=REP_CHOICES, default="both")
    PARTY_CHOICES = [
        ('d', 'Democrat'),
        ('r', 'Republican'),
        ('all', 'All'),
    ]
    party = models.CharField(max_length=10, choices=PARTY_CHOICES, default="all")
    POSITION_CHOICES = [
        ('for', 'For'),
        ('against', 'Against'),
        ('undecided', 'Undecided'),
        ('unknown', 'Position unknown'),
        ('all', 'All'),
    ]
    position = models.CharField(max_length=9, choices=POSITION_CHOICES, default="unknown")
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
        if self.script_type != "default":
            return
        return {'rep': {'full_appellation': 'Default Script', 'phone': 'N/A'},
            'script_type': self.script_type, 'priority': int(self.priority),
            'content': self.content }

    def get_universal_scripts(self):
        if self.script_type != "universal":
            return
        scripts = []
        for rep in self.get_always_reps_as_models():
            scripts.append({'rep': rep, 'script_type': self.script_type,
                'priority': int(self.priority), 'content': self.content })
        return scripts

    def does_rep_meet_conditions(self, rep):
        '''Checks if the script's conditions match a given legislator'''

        # Representative type
        if self.rep_type.lower() != rep.title.lower():
            return False

        # Party type
        if self.party.lower() != rep.party.lower():
            return False

        # Position
        # TODO: check ScriptMatcher object

        # Committees
        # TODO: need to do a separate query for this

        # States
        if self.states:
            if rep.state not in self.get_states():
                return False

        # Districts
        # TODO: what would this actually be used for?  Can ppl just pick based on
        # congressfolk (reusing always_reps?)?  Do we want a "swing district" boolean
        # option?

        return True

        # Add method which updates ScriptMatcher when script is updated.
        # How?  Finds all ScriptMatchers matched to this script?

POSITION_CHOICES = [
    ('for', 'For'),
    ('against', 'Against'),
    ('undecided', 'Undecided'),
    ('unknown', 'Position unknown'),
    ('all', 'All'),
]

class ScriptMatcher(models.Model):
    '''Creates links between action & legislator, with optional link to phonescript'''
    legislator = models.ForeignKey(Legislator)
    action = models.ForeignKey(Action)
    script = models.ForeignKey(PhoneScript, blank=True, null=True)
    position = models.CharField(max_length=9, choices=POSITION_CHOICES, default="unknown")
    notes = models.CharField(max_length=200, blank=True, null=True)

    # Add save method catch of when position is changed, re run the "get script to use"
    # function

    def __unicode__(self):
        script = self.script if self.script else ""
        return "%s %s (%s)" % (self.legislator, self.action, script)
