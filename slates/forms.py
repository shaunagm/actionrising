from django.forms import ModelForm, MultipleChoiceField
from datetimewidget.widgets import DateTimeWidget

from actions.models import Action
from mysite.lib.choices import PRIVACY_CHOICES
from mysite.lib.privacy import get_global_privacy_default
from slates.models import Slate, SlateActionRelationship

class SlateForm(ModelForm):
    actions = MultipleChoiceField(required=False)

    class Meta:
        model = Slate
        fields = ['title', 'description', 'status', 'privacy', 'actions']

    def __init__(self, user, *args, **kwargs):
        super(SlateForm, self).__init__(*args, **kwargs)
        # TODO For the editform, this will not show any actions that have since been finished/withdrawn.
        # May want to override that behavior and populate the queryset with open actions
        # plus currently linked actions?
        self.fields['actions'].queryset = Action.objects.filter(status="rea").filter(current_privacy__in=["pub", "sit"]).order_by("title")
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], PRIVACY_CHOICES[2], ('inh', get_global_privacy_default(user.profile, "decorated")))
        self.fields['privacy'].choices = NEW_CHOICES

class SlateActionRelationshipForm(ModelForm):

    class Meta:
        model = SlateActionRelationship
        fields = ['priority', 'status', 'notes']
