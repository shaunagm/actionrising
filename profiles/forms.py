from django.forms import ModelForm, ModelMultipleChoiceField, ChoiceField, Select
from django.forms import inlineformset_factory
from django.forms.widgets import HiddenInput

from mysite.utils import PRIVACY_DEFAULT_CHOICES
from profiles.models import Profile, ProfileActionRelationship, PrivacyDefaults

class ProfileForm(ModelForm):
    privacy_default = ChoiceField(label='Default privacy setting',
                                widget=Select(),
                                choices=PRIVACY_DEFAULT_CHOICES,
                                required=True)

    class Meta:
        model = Profile
        fields = ['description', 'location']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['privacy_default'].help_text = 'This setting will apply to all actions and slates you create unless you override them individually.'
        self.fields['privacy_default'].initial = self.instance.privacy_defaults.global_default

    def save(self, commit=True):
        self.instance.privacy_defaults.global_default = self.cleaned_data['privacy_default']
        self.instance.privacy_defaults.save()
        return super(ProfileForm, self).save(commit=commit)

class ProfileActionRelationshipForm(ModelForm):
    profiles = ModelMultipleChoiceField(queryset=Profile.objects.all(), label="Suggest to friends", required=False)
    # slates = ModelMultipleChoiceField(label="Add to slates", required=False)

    class Meta:
        model = ProfileActionRelationship
        fields = ['priority', 'privacy', 'status']

    def __init__(self, *args, **kwargs):
        if 'par' in kwargs:
            par = kwargs.pop('par')
            super(ProfileActionRelationshipForm, self).__init__(*args, **kwargs)
            self.fields['profiles'].queryset = par.profile.get_followers()
            # self.fields['slates'].queryset = par.profile.slates.all()
        else:
            super(ProfileActionRelationshipForm, self).__init__(*args, **kwargs)
