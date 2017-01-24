from django.forms import ModelForm, MultipleChoiceField
from datetimewidget.widgets import DateTimeWidget
from django.forms.widgets import HiddenInput

from actions.models import Action
from tags.lib import tag_helpers
from mysite.lib.choices import PRIVACY_CHOICES
from mysite.lib.privacy import get_global_privacy_default
from plugins import plugin_helpers

class ActionForm(ModelForm):

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

        # Handle action queryset

        # Handle tags
        tags, form = tag_helpers.get_tags_from_valid_form(self)
        tag_helpers.add_tags_to_object(instance, tags)

        # Handle plugins
        plugin_helpers.process_plugin_fields(self, instance)

        return instance
