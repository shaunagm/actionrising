from django.forms import Form, ModelForm, ModelMultipleChoiceField, HiddenInput
from datetimewidget.widgets import DateTimeWidget
from guardian.shortcuts import (get_groups_with_perms, get_users_with_perms,
    assign_perm, remove_perm, get_perms)
from django.contrib.auth.models import User, Group

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

class SlateAdminForm(Form):
    group_contributors = ModelMultipleChoiceField(label="Groups whose members can contribute to this slate",
        required=False, queryset=Group.objects.all())
    user_contributors = ModelMultipleChoiceField(label="Individual users who can contribute to this slate",
        required=False, queryset=User.objects.all())
    group_admins = ModelMultipleChoiceField(label="Groups whose members are admins for this slate",
        required=False, queryset=Group.objects.all())
    user_admins = ModelMultipleChoiceField(label="Individual users who are admins for this slate",
        required=False, queryset=User.objects.all())

    def __init__(self, slate, user, *args, **kwargs):
        super(SlateAdminForm, self).__init__(*args, **kwargs)
        self.user = user
        self.slate = slate
        self.is_owner = self.user == self.slate.creator

        self.starting_group_contributors, self.starting_group_admins = [], []
        for group, value in get_groups_with_perms(self.slate, attach_perms=True).items():
            if 'contribute_actions' in value:
                self.starting_group_contributors.append(group)
            if 'administer_slate' in value:
                self.starting_group_admins.append(group)
        self.fields['group_contributors'].initial = self.starting_group_contributors
        self.fields['group_admins'].initial = self.starting_group_admins

        self.starting_user_contributors, self.starting_user_admins = [], []
        for user, value in get_users_with_perms(self.slate, attach_perms=True).items():
            if 'contribute_actions' in value:
                self.starting_user_contributors.append(user)
            if 'administer_slate' in value:
                self.starting_user_admins.append(user)
        self.fields['user_contributors'].initial = self.starting_user_contributors
        self.fields['user_admins'].initial = self.starting_user_admins

        if not self.is_owner:
            self.fields['group_admins'].widget = HiddenInput()
            self.fields['user_admins'].widget = HiddenInput()

    def process_form(self):

        # Group Contributors
        new_group_contribs = self.cleaned_data.pop('group_contributors')
        group_contribs_to_remove = list(set(self.starting_group_contributors) -
                                        set(new_group_contribs))
        for new_group_contrib in new_group_contribs:
            assign_perm('contribute_actions', new_group_contrib, self.slate)
        for old_group_contrib in group_contribs_to_remove:
            remove_perm('contribute_actions', old_group_contrib, self.slate)

        # User Contributors
        new_user_contribs = self.cleaned_data.pop('user_contributors')
        user_contribs_to_remove = list(set(self.starting_user_contributors) -
                                       set(new_user_contribs))
        for new_user_contrib in new_user_contribs:
            assign_perm('contribute_actions', new_user_contrib, self.slate)
        for old_user_contrib in user_contribs_to_remove:
            remove_perm('contribute_actions', old_user_contrib, self.slate)

        if self.is_owner:

            # Group Admins
            new_group_admins = self.cleaned_data.pop('group_admins')
            group_admins_to_remove = list(set(self.starting_group_admins) -
                                          set(new_group_admins))
            for new_group_admin in new_group_admins:
                assign_perm('administer_slate', new_group_admin, self.slate)
            for old_group_admin in group_admins_to_remove:
                remove_perm('administer_slate', old_group_admin, self.slate)

            # User Admins
            new_user_admins = self.cleaned_data.pop('user_admins')
            user_admins_to_remove = list(set(self.starting_user_admins) -
                                         set(new_user_admins))
            for new_user_admin in new_user_admins:
                assign_perm('administer_slate', new_user_admin, self.slate)
            for old_user_admin in user_admins_to_remove:
                remove_perm('administer_slate', old_user_admin, self.slate)
