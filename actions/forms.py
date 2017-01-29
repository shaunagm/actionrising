from django import forms
from datetimewidget.widgets import DateTimeWidget
from django.forms.widgets import HiddenInput

from actions.models import Action
from tags.lib import tag_helpers
from mysite.lib.choices import PRIVACY_CHOICES
from mysite.lib.privacy import get_global_privacy_default
from plugins import plugin_helpers

class ActionForm(forms.ModelForm):

    class Meta:
        model = Action
        fields = ['title', 'anonymize', 'description', 'privacy', 'priority', 'duration',
            'status', 'deadline']
        widgets = {
            'deadline': DateTimeWidget(options={'format': 'mm/dd/yyyy HH:mm'}, bootstrap_version=3),
        }
        help_texts = {
            'anonymize': 'Show "anonymous" as creator. (Note: this changes the display only, and you can change your mind and choose to show your username later.)',
            'deadline': 'MM/DD/YYYY HH:MM:SS (hours, minutes and seconds optional, defaults to midnight)'
            }

    def __init__(self, user, formtype, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.user = user
        self.formtype = formtype
        if self.formtype == "create":
            self.fields['status'].widget = HiddenInput()

        # Set privacy
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], PRIVACY_CHOICES[2], ('inh', get_global_privacy_default(user.profile, "decorated")))
        self.fields['privacy'].choices = NEW_CHOICES

        # Set tags
        self.fields = tag_helpers.add_tag_fields_to_form(self.fields, self.instance, formtype)

        # Set plugin fields
        self = plugin_helpers.add_plugin_fields(self)

    def save(self, commit=True):
        instance = super(ActionForm, self).save(commit=False)

        # Add user if created, then save
        if self.formtype == "create":
            instance.creator = self.user
        instance.save()

        # Handle tags
        tags, form = tag_helpers.get_tags_from_valid_form(self)
        tag_helpers.add_tags_to_object(instance, tags)

        # Handle plugins
        plugin_helpers.process_plugin_fields(self, instance)

        return instance


# Filter Wizard Forms
end_early_field = forms.BooleanField(widget=HiddenInput(attrs={'id': 'end_early_field'}),
    required=False, initial=False)

class FilterWizard_Kind(forms.Form):
    end_early = end_early_field
    question = "What kinds of actions do you want to hear about?"
    kinds = forms.CharField(max_length=100) # Should be choice field

    def filter_results(self, wizard, results):
        data_dict = wizard.get_form_step_data(self)
        return Action.objects.filter(tags__in=data_dict['0-kinds'])

class FilterWizard_Topic(forms.Form):
    end_early = end_early_field
    question = "What topics are you most interested in?"
    topics = forms.CharField(max_length=100) # Should be choice field

    def filter_results(self, old_data, new_data):
        search_terms = new_data['1-topics']
        print(old_data)
        # Can't use filter here as is, because old_results is now a list
        return old_data.filter(tags__in=search_terms)

class FilterWizard_Time(forms.Form):
    end_early = end_early_field
    question = "How much time can you spend on the action?"
    time = forms.CharField(max_length=100) # Should be choice field

class FilterWizard_Deadline(forms.Form):
    end_early = end_early_field
    question = "Should we prioritize actions that need to be done soon, or actions without a deadline?"
    deadline = forms.CharField(max_length=100) # Should be choice field

class FilterWizard_Location(forms.Form):
    end_early = end_early_field
    question = "Should we limit actions to local actions, state actions, or national actions?"
    location = forms.CharField(max_length=100) # Should be choice field
    # Should check if user has location set

class FilterWizard_Friends(forms.Form):
    end_early = end_early_field
    question = "Should we prioritize actions created by or recommended by the people you follow?"
    friends = forms.CharField(max_length=100) # Should be choice field
