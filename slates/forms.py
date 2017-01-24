from django.forms import ModelForm, ModelMultipleChoiceField
from datetimewidget.widgets import DateTimeWidget

from actions.models import Action
from mysite.lib.choices import PRIVACY_CHOICES
from mysite.lib.privacy import get_global_privacy_default
from slates.models import Slate, SlateActionRelationship
from slates.lib import slate_helpers
from tags.lib import tag_helpers
from plugins import plugin_helpers

class SlateForm(ModelForm):
    actions = ModelMultipleChoiceField(queryset=Action.objects.all(), required=False)

    class Meta:
        model = Slate
        fields = ['title', 'description', 'status', 'privacy', 'actions']

    def __init__(self, user, formtype, *args, **kwargs):
        super(SlateForm, self).__init__(*args, **kwargs)
        self.user = user
        self.formtype = formtype

        # Set actions queryset
        self.fields['actions'].queryset = Action.objects.filter(status="rea").filter(current_privacy__in=["pub", "sit"]).order_by("title")
        if self.formtype == "update":
            self.fields['actions'].initial = self.instance.actions.all()

        # Set privacy
        NEW_CHOICES = (PRIVACY_CHOICES[0], PRIVACY_CHOICES[1], PRIVACY_CHOICES[2], ('inh', get_global_privacy_default(user.profile, "decorated")))
        self.fields['privacy'].choices = NEW_CHOICES

        # Set tags
        self.fields = tag_helpers.add_tag_fields_to_form(self.fields, self.instance, formtype)

        # Set plugin
        self = plugin_helpers.add_plugin_fields(self)

    def save(self, commit=True):
        instance = super(SlateForm, self).save(commit=False)

        # Add user if created, then save
        if self.formtype == "create":
            instance.creator = self.user
        instance.save()

        # Manage action queryset
        actions = self.cleaned_data.pop('actions')
        slate_helpers.manage_actions(self.formtype, instance, actions)

        # Handle tags
        tags, form = tag_helpers.get_tags_from_valid_form(self)
        tag_helpers.add_tags_to_object(instance, tags)

        # Handle plugins
        plugin_helpers.process_plugin_fields(self, instance)

        return instance

class SlateActionRelationshipForm(ModelForm):

    class Meta:
        model = SlateActionRelationship
        fields = ['priority', 'status', 'notes']
