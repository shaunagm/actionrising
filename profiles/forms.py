from django.forms import ModelForm, ModelMultipleChoiceField
from django.forms import inlineformset_factory
from django.forms.widgets import HiddenInput

from profiles.models import Profile, ProfileActionRelationship
# from actions.models import Slate

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
