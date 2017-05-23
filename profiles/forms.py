from django.utils.translation import ugettext as _
from collections import OrderedDict
from django.forms import (ModelForm, ModelMultipleChoiceField, ModelChoiceField,
    ChoiceField, Select, CharField, SelectMultiple)
from django.forms import inlineformset_factory
from django.forms.widgets import HiddenInput

from mysite.lib.choices import PrivacyChoices
from mysite.lib.privacy import get_global_privacy_default
from profiles.models import (Profile, ProfileActionRelationship, PrivacyDefaults)
from slates.models import Slate
from plugins import plugin_helpers

class ProfileForm(ModelForm):
    first_name = CharField(max_length=30, required=False, label="First name")
    last_name = CharField(max_length=30, required=False, label="Last name")
    privacy_default = ChoiceField(label='Default privacy setting',
                                widget=Select(),
                                choices=PrivacyChoices.default_choices(),
                                required=True)

    class Meta:
        model = Profile
        fields = ['description', 'privacy']

    def __init__(self, initial, instance, **kwargs):
        initial.setdefault('first_name', instance.user.first_name)
        initial.setdefault('last_name', instance.user.last_name)
        initial.setdefault('privacy_default', instance.privacy_defaults.global_default)

        super(ProfileForm, self).__init__(initial=initial, instance=instance, **kwargs)

        # Set privacy
        self.fields['privacy_default'].help_text = 'This setting will apply to all actions and slates you create unless you override them individually.'
        self.fields['privacy'].choices = PrivacyChoices.personalized(get_global_privacy_default(self.instance, "decorated"))

        # Set plugin fields
        self = plugin_helpers.add_plugin_fields(self)

    def save(self, commit=True):
        instance = super(ProfileForm, self).save(commit=commit)

        # Handle usernames
        if self.cleaned_data['first_name'] or self.cleaned_data['last_name']:
            instance.user.first_name = self.cleaned_data['first_name']
            instance.user.last_name = self.cleaned_data['last_name']
            instance.user.save()

        # Handle privacy
        instance.privacy_defaults.global_default = self.cleaned_data['privacy_default']
        instance.privacy_defaults.save()

        # Handle plugins
        plugin_helpers.process_plugin_fields(self, instance)

        return instance

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
            self.fields['profiles'].queryset = par.profile.get_followers
            self.fields['slates'].queryset = par.profile.user.slate_set.all()
        else:
            super(ProfileActionRelationshipForm, self).__init__(*args, **kwargs)
