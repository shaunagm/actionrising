from django import forms
from plugins.phonescript_plugin.models import (PhoneScript, Legislator, ScriptMatcher,
    POSITION_CHOICES)
from actions.models import Action

class DefaultForm(forms.ModelForm):

    class Meta:
        model = PhoneScript
        fields = ['content', 'priority']

    def save(self, action, commit=True):
        instance = super(DefaultForm, self).save(commit=False)
        instance.action = action
        instance.script_type = "default"
        instance.save()

class ConstituentForm(forms.ModelForm):

    class Meta:
        model = PhoneScript
        fields = ['content', 'priority', 'rep_type', 'party', 'position']
        # fields = ['content', 'priority', 'rep_type', 'party', 'position',
        #     'committees', 'states', 'districts']
        labels = {
            'content': 'Text of phonescript',
        }

    def save(self, action=None, commit=True):
        instance = super(ConstituentForm, self).save(commit=False)
        instance.action = action
        instance.script_type = "constituent"
        instance.save()

ConstituentFormset = forms.modelformset_factory(PhoneScript, ConstituentForm, extra=10)

class UniversalForm(forms.ModelForm):

    class Meta:
        model = PhoneScript
        fields = ['content', 'always_reps', 'priority']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs.update(initial={'always_reps': instance.get_always_reps()})
        super(UniversalForm, self).__init__(*args, **kwargs)
        self.fields['always_reps'].label = 'Specific people to show this script for'
        self.fields['always_reps'].widget = forms.SelectMultiple(choices=[(i.pk, i.full_appellation()) for i in Legislator.objects.all()])

    def save(self, action=None, commit=True):
        instance = super(UniversalForm, self).save(commit=False)
        instance.action = action
        instance.script_type = "universal"
        instance.save()
        # TODO: if reps have been removed, delete

UniversalFormset = forms.modelformset_factory(PhoneScript, UniversalForm, extra=10)

class LegislatorPositionForm(forms.Form):

    def __init__(self, action_slug, *args, **kwargs):
       super(LegislatorPositionForm, self).__init__(*args, **kwargs)
       self.action = Action.objects.get(slug=action_slug)
       sm_set = ScriptMatcher.objects.filter(action=self.action)
       # TO DO: get these in a reasonable order, split by Sen + House at least, maybe also party
       for sm in sm_set:
           field_name = "smdata_" + sm.legislator.bioguide_id
           self.fields[field_name + "_leg"] = forms.CharField(initial=sm.legislator,
                disabled=True, label="")
           self.fields[field_name + "_pos"] = forms.ChoiceField(choices=POSITION_CHOICES[:4],
                label="Position", required=False)
           self.initial[field_name + "_pos"] = sm.position
           self.fields[field_name + "_not"] = forms.CharField(initial=sm.notes,
                label="Notes", max_length=200, required=False)


    # def save(self, request, commit=True):
    #     user = request.user
    #     data = self.cleaned_data
    #     print(data)
