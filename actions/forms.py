from django.forms import ModelForm

from actions.models import Action, Slate

class ActionForm(ModelForm):

    class Meta:
        model = Action
        fields = ['slug', 'title', 'anonymize', 'main_link', 'text', 'privacy', 'location', 'status', 'has_deadline', 'deadline', 'topics', 'actiontypes']

    def __init__(self, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs['placeholder'] = 'please-use-alphanumerics-and-dashes-only'


class SlateForm(ModelForm):

    class Meta:
        model = Slate
        fields = fields = ['slug', 'title', 'text', 'status', 'privacy', 'actions']

    def __init__(self, *args, **kwargs):
        super(SlateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs['placeholder'] = 'please-use-alphanumerics-and-dashes-only'
