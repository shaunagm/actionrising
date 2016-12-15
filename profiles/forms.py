from django.forms import ModelForm, ModelMultipleChoiceField, ModelChoiceField, ChoiceField, Select
from django.forms import inlineformset_factory
from django.forms.widgets import HiddenInput

from mysite.utils import (PRIVACY_DEFAULT_CHOICES, PRIVACY_CHOICES,
    get_global_privacy_default, get_global_privacy_string)
from profiles.models import Profile, ProfileActionRelationship, PrivacyDefaults
from actions.models import Slate

class ProfileForm(ModelForm):
    privacy_default = ChoiceField(label='Default privacy setting',
                                widget=Select(),
                                choices=PRIVACY_DEFAULT_CHOICES,
                                required=True)

    class Meta:
        model = Profile
        fields = ['description', 'privacy', 'location']

    def __init__(self, user, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['privacy_default'].help_text = 'This setting will apply to all actions and slates you create unless you override them individually.'
        self.fields['privacy_default'].initial = self.instance.privacy_defaults.global_default
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], PRIVACY_CHOICES[2], ('inh', get_global_privacy_string(user.profile)))
        self.fields['privacy'].choices = NEW_CHOICES

    def save(self, commit=True):
        self.instance.privacy_defaults.global_default = self.cleaned_data['privacy_default']
        self.instance.privacy_defaults.save()
        return super(ProfileForm, self).save(commit=commit)

class SlateChoiceField(ModelMultipleChoiceField):
   def label_from_instance(self, obj):
        return obj.title

class PrivacyChoiceField(ModelChoiceField):
   def label_from_instance(self, obj):
        return obj.get_privacy_string()

class ProfileActionRelationshipForm(ModelForm):
    profiles = ModelMultipleChoiceField(queryset=Profile.objects.all(), label="Suggest to friends", required=False)
    slates = SlateChoiceField(queryset=Slate.objects.all(), label="Add to slates", required=False)

    class Meta:
        model = ProfileActionRelationship
        fields = ['priority', 'status', 'notes']

    def __init__(self, *args, **kwargs):
        if 'par' in kwargs:
            par = kwargs.pop('par')
            super(ProfileActionRelationshipForm, self).__init__(*args, **kwargs)
            self.fields['profiles'].queryset = par.profile.get_followers()
            self.fields['slates'].queryset = par.profile.user.slate_set.all()
        else:
            super(ProfileActionRelationshipForm, self).__init__(*args, **kwargs)
