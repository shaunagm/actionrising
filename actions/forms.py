from django.forms import ModelForm

from datetimewidget.widgets import DateTimeWidget

from actions.models import Action, Slate, SlateActionRelationship
from mysite.utils import (PRIVACY_CHOICES, get_global_privacy_string)

class ActionForm(ModelForm):

    class Meta:
        model = Action
        fields = ['title', 'anonymize', 'main_link', 'description', 'privacy', 'priority', 'location', 'status', 'deadline', 'topics', 'actiontypes']
        widgets = {
            'deadline': DateTimeWidget(options={'format': 'mm/dd/yyyy HH:mm'}, bootstrap_version=3),
        }
        help_texts = {
            'anonymize': 'Show "anonymous" as creator. (Note: this changes the display only, and you can change your mind and choose to show your username later.)',
            'topics': "Don't see the topic you need?  Request a new topic <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.",
            'actiontypes': "Don't see the type of action you need?  Request a new action type <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.",
        }

    def __init__(self, user, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs['placeholder'] = 'MM/DD/YYYY HH:MM:SS (hours, minutes and seconds optional, defaults to midnight)'
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], ('inh', get_global_privacy_string(user.profile)))
        self.fields['privacy'].choices = NEW_CHOICES
        self.fields['actiontypes'].label = "Types of action"

class SlateForm(ModelForm):

    class Meta:
        model = Slate
        fields = fields = ['title', 'description', 'status', 'privacy', 'actions']

    def __init__(self, user, *args, **kwargs):
        super(SlateForm, self).__init__(*args, **kwargs)
        # TODO For the editform, this will not show any actions that have since been finished/withdrawn.
        # May want to override that behavior and populate the queryset with open actions
        # plus currently linked actions?
        self.fields['actions'].queryset = Action.objects.filter(status="rea").order_by("title")
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], ('inh', get_global_privacy_string(user.profile)))
        self.fields['privacy'].choices = NEW_CHOICES

class SlateActionRelationshipForm(ModelForm):

    class Meta:
        model = SlateActionRelationship
        fields = ['priority', 'privacy', 'status', 'notes']

    def __init__(self, *args, **kwargs):
        if 'sar' in kwargs:
            sar = kwargs.pop('sar')
            super(SlateActionRelationshipForm, self).__init__(*args, **kwargs)
            NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], ('inh', get_global_privacy_string(sar)))
            self.fields['privacy'].choices = NEW_CHOICES
        else:
            super(SlateActionRelationshipForm, self).__init__(*args, **kwargs)
