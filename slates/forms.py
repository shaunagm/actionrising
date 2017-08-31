from django.forms import ModelForm, ModelMultipleChoiceField, HiddenInput
from datetimewidget.widgets import DateTimeWidget
from guardian.shortcuts import get_groups_with_perms, assign_perm, remove_perm

from actions.models import Action
from mysite.lib.choices import PrivacyChoices, StatusChoices
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

        # If user is not owner, hide title
        if self.formtype == "update" and self.user != self.instance.creator:
            self.fields['title'].widget = HiddenInput()


        # Set actions queryset
        self.fields['actions'].queryset = Action.objects.filter(status=StatusChoices.ready).filter(current_privacy__in=[PrivacyChoices.public, PrivacyChoices.sitewide]).order_by("title")
        if self.formtype == "update":
            self.fields['actions'].initial = self.instance.actions.all()

        # Set privacy
        self.fields['privacy'].choices = PrivacyChoices.personalized_with_groups(get_global_privacy_default(user.profile, "decorated"))

        # Set potential groups
        help_text = "Select some groups" if self.user.groups.all() else "You have no groups to select"
        self.fields['groups'] = ModelMultipleChoiceField(label="Groups that can access this slate",
            required=False, queryset=self.user.groups.all(), help_text=help_text)
        if self.formtype == "update":
            self.fields['groups'].initial = get_groups_with_perms(self.instance)

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

        # Handle groups
        if instance.privacy == "members":
            new_groups = self.cleaned_data.pop('groups')
            groups_to_remove = list(set(get_groups_with_perms(instance)) - set(new_groups))
            for new_group in new_groups:
                assign_perm('view_slate', new_group, instance)
            for old_group in groups_to_remove:
                remove_perm('view_slate', old_group, instance)
        else:
            old_groups = get_groups_with_perms(instance)
            [remove_perm('view_slate', old_group, instance) for old_group in old_groups]

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
