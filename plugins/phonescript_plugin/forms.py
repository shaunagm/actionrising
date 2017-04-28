from django import forms
from plugins.phonescript_plugin.models import (PhoneScript, Legislator, ScriptMatcher,
    PositionChoices, TypeChoices)
from plugins.phonescript_plugin.lib import phonescripts
from actions.models import Action

class DefaultForm(forms.ModelForm):
    content = forms.CharField(max_length=1000, required=False) # Allows the form to validate when not filled out

    class Meta:
        model = PhoneScript
        fields = ['content', 'priority']

    def save(self, action, commit=True):
        instance = super(DefaultForm, self).save(commit=False)
        if instance.content not in [None, "", []]:
            instance.action = action
            instance.script_type = TypeChoices.default
            instance.save()

class ConstituentForm(forms.ModelForm):

    class Meta:
        model = PhoneScript
        fields = ['content', 'priority', 'rep_type', 'party', 'position']
        labels = {
            'content': 'Text of phonescript',
        }

    def save(self, action=None, commit=True):
        instance = super(ConstituentForm, self).save(commit=False)
        instance.action = action
        instance.script_type = TypeChoices.constituent
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
        legislators = Legislator.objects.filter(in_office=True)
        if legislators.count < 1:
            legislators = phonescripts.create_legislators()
        self.fields['always_reps'].label = 'Specific people to show this script for'
        self.fields['always_reps'].widget = forms.SelectMultiple(choices=[(i.pk, i.full_appellation()) for i in legislators])

    def save(self, action=None, commit=True):
        instance = super(UniversalForm, self).save(commit=False)
        instance.action = action
        instance.script_type = TypeChoices.universal
        instance.save()
        # TODO: if reps have been removed, delete

UniversalFormset = forms.modelformset_factory(PhoneScript, UniversalForm, extra=10)

class ReadOnlyText(forms.TextInput):
    '''Read only field that displays as text for use in LegislatorPositionForm.'''
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return value

class LegislatorPositionForm(forms.Form):

    def __init__(self, action_slug, *args, **kwargs):
       super(LegislatorPositionForm, self).__init__(*args, **kwargs)
       self.action = Action.objects.get(slug=action_slug)
       sm_set = ScriptMatcher.objects.filter(action=self.action)
       # TO DO: get these in a reasonable order, split by Sen + House at least, maybe also party
       for sm in sm_set:
           field_name = "smdata_" + sm.legislator.bioguide_id
           self.fields[field_name + "_leg"] = forms.CharField(initial=sm.legislator,
                disabled=True, label="", widget=ReadOnlyText)
           self.fields[field_name + "_pos"] = forms.ChoiceField(choices=PositionChoices.choices[:4],
                label="Position", required=False)
           self.initial[field_name + "_pos"] = sm.position
           self.fields[field_name + "_not"] = forms.CharField(initial=sm.notes,
                label="Notes", max_length=200, required=False)


    # def save(self, request, commit=True):
    #     user = request.user
    #     data = self.cleaned_data
    #     print(data)
