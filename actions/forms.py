from django.forms import ModelForm, MultipleChoiceField
from datetimewidget.widgets import DateTimeWidget
from django.forms.widgets import HiddenInput

from actions.models import Action
from tags.models import Tag
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
        # Move creation of fields to __init__ (and maybe eventually to own form?) so they're not
        # imported and run during migrations
        self.fields['type_tags'] = MultipleChoiceField(label="Types of action", required=False,
            choices=[(i.pk, i.name) for i in Tag.objects.filter(kind="type")],
            help_text="Don't see the topic you need?  Request a new topic <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.")
        self.fields['topic_tags'] = MultipleChoiceField(label="Action topics", required=False,
            choices=[(i.pk, i.name) for i in Tag.objects.filter(kind="topic")],
            help_text="Don't see the type of action you need?  Request a new action type <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.")
        self.fields['goal_tags'] =  MultipleChoiceField(label="Goals of action", required=False,
            choices=[(i.pk, i.name) for i in Tag.objects.filter(kind="goal")],
            help_text="Don't see the action goal you need?  Request a new goal <a href='https://goo.gl/forms/g5AT4GdTXqcNi62q1'>here</a>.")
        if formtype == "create":
            self.fields['status'].widget = HiddenInput()
        else:
            self.fields['topic_tags'].initial = [tag.pk for tag in self.instance.action_tags.filter(kind="topic")]
            self.fields['type_tags'].initial = [tag.pk for tag in self.instance.action_tags.filter(kind="type")]
            self.fields['goal_tags'].initial = [tag.pk for tag in self.instance.action_tags.filter(kind="goal")]
