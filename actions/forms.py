from django.forms import ModelForm, MultipleChoiceField
from datetimewidget.widgets import DateTimeWidget
from django.forms.widgets import HiddenInput

from actions.models import Action
from tags.models import Tag
from tags.lib import tag_helpers
from mysite.lib.choices import PRIVACY_CHOICES
from mysite.lib.privacy import get_global_privacy_default

class ActionForm(ModelForm):

    class Meta:
        model = Action
        fields = ['title', 'anonymize', 'description', 'privacy', 'priority', 'duration',
            'location', 'status', 'deadline']
        widgets = {
            'deadline': DateTimeWidget(options={'format': 'mm/dd/yyyy HH:mm'}, bootstrap_version=3),
        }
        help_texts = {
            'anonymize': 'Show "anonymous" as creator. (Note: this changes the display only, and you can change your mind and choose to show your username later.)',
            }

    def __init__(self, user, formtype, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs['placeholder'] = 'MM/DD/YYYY HH:MM:SS (hours, minutes and seconds optional, defaults to midnight)'
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], PRIVACY_CHOICES[2], ('inh', get_global_privacy_default(user.profile, "decorated")))
        self.fields['privacy'].choices = NEW_CHOICES
        self.fields = tag_helpers.add_tag_fields_to_form(self.fields, self.instance, formtype)
        if formtype == "create":
            self.fields['status'].widget = HiddenInput()
