from django.forms import ModelForm

from datetimewidget.widgets import DateTimeWidget

from actions.models import Action, Slate

class ActionForm(ModelForm):

    class Meta:
        model = Action
        fields = ['title', 'anonymize', 'main_link', 'description', 'privacy', 'priority', 'location', 'status', 'deadline', 'topics', 'actiontypes']
        widgets = {
            'deadline': DateTimeWidget(options={'format': 'mm/dd/yyyy HH:mm'}, bootstrap_version=3),
        }
        help_texts = {
            'anonymize': 'Show "anonymous" as creator. (Note: this changes the display only, and you can change your mind and choose to show your username later.)',
            'privacy': 'Choosing "inherit" means privacy will be set to whatever your privacy default is, and will change if your default changes.  You can change your privacy default by editing your profile.'
        }

    def __init__(self, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs['placeholder'] = 'MM/DD/YYYY HH:MM:SS (hours, minutes and seconds optional, defaults to midnight)'

class SlateForm(ModelForm):

    class Meta:
        model = Slate
        fields = fields = ['title', 'description', 'status', 'privacy', 'actions']
        help_texts = {
            'privacy': 'Choosing "inherit" means privacy will be set to whatever your privacy default is, and will change if your default changes.  You can change your privacy default by editing your profile.'
        }

    def __init__(self, *args, **kwargs):
        super(SlateForm, self).__init__(*args, **kwargs)
        # TODO For the editform, this will not show any actions that have since been finished/withdrawn.
        # May want to override that behavior and populate the queryset with open actions
        # plus currently linked actions?
        self.fields['actions'].queryset = Action.objects.filter(status="rea").order_by("title")
