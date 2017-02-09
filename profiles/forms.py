from django.utils.translation import ugettext as _
from collections import OrderedDict
from django.forms import (ModelForm, ModelMultipleChoiceField, ModelChoiceField,
    ChoiceField, Select, CharField, SelectMultiple)
from django.forms import inlineformset_factory
from django.forms.widgets import HiddenInput

from mysite.lib.choices import PRIVACY_DEFAULT_CHOICES, PRIVACY_CHOICES
from mysite.lib.privacy import get_global_privacy_default
from profiles.models import (Profile, ProfileActionRelationship, PrivacyDefaults,
    NavbarSettings)
from slates.models import Slate
from plugins import plugin_helpers

class ProfileForm(ModelForm):
    first_name = CharField(max_length=30, required=False, label="First name")
    last_name = CharField(max_length=30, required=False, label="Last name")
    privacy_default = ChoiceField(label='Default privacy setting',
                                widget=Select(),
                                choices=PRIVACY_DEFAULT_CHOICES,
                                required=True)

    class Meta:
        model = Profile
        fields = ['description', 'privacy']

    def __init__(self, user, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # Set privacy
        self.fields['privacy_default'].help_text = 'This setting will apply to all actions and slates you create unless you override them individually.'
        self.fields['privacy_default'].initial = self.instance.privacy_defaults.global_default
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], PRIVACY_CHOICES[2], ('inh', get_global_privacy_default(user.profile, "decorated")))
        self.fields['privacy'].choices = NEW_CHOICES

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
            self.fields['profiles'].queryset = par.profile.get_followers()
            self.fields['slates'].queryset = par.profile.user.slate_set.all()
        else:
            super(ProfileActionRelationshipForm, self).__init__(*args, **kwargs)

LINK_CHOICES = (
    ('dash', _('Your Dashboard')),
    ('findactions', _('Find Actions Landing Page')),
    ('createactions', _('Create Actions Landing Page')),
    ('openactions', _('Your Open Actions')),
    ('allactions', _('All Actions')),
    ('addaction', _('Create An Action')),
    ('feed', _('Your Feed')),
)

LANDING_LINK_CHOICES = (
    ('dash', _('Your Dashboard')),
    ('actions', _('Search Actions')),
    ('feed', _('Your Feed')),
)

class NavbarForm(ModelForm):
    links = CharField(widget=SelectMultiple(choices=LINK_CHOICES), required=False)
    landing_link = CharField(widget=SelectMultiple(choices=LANDING_LINK_CHOICES), required=False)

    class Meta:
        model = NavbarSettings
        fields = ["use_default", "links", "use_default_landing", "landing_link"]

    def __init__(self, *args, **kwargs):
        super(NavbarForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            self.initial['links'] = self.instance.get_links()
            self.initial['landing_link'] = self.instance.get_landing_link()
        self.fields['use_default'].label = "Use the default navbar"
        self.fields['links'].label = "Select up to four links to show in your navbar"
        self.fields['use_default_landing'].label = "Use the default landing page"
        self.fields['landing_link'].label = "Select a link to use as your landing page"
