from django.forms import ModelForm

from datetimewidget.widgets import DateTimeWidget

from actions.models import Action, Slate

class ActionForm(ModelForm):

    class Meta:
        model = Action
        fields = ['slug', 'title', 'anonymize', 'main_link', 'text', 'privacy', 'location', 'status', 'has_deadline', 'deadline', 'topics', 'actiontypes']
        widgets = {
            'deadline': DateTimeWidget(bootstrap_version=3),
        }

    def __init__(self, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs['placeholder'] = 'please-use-alphanumerics-and-dashes-only'
        self.fields['deadline'].widget.attrs['placeholder'] = 'MM/DD/YYYY HH:MM:SS (hours, minutes and seconds optional, defaults to midnight)'

class SlateForm(ModelForm):

    class Meta:
        model = Slate
        fields = fields = ['slug', 'title', 'text', 'status', 'privacy', 'actions']

    def __init__(self, *args, **kwargs):
        super(SlateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs['placeholder'] = 'please-use-alphanumerics-and-dashes-only'
