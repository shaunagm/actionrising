from django import forms
from django.forms.widgets import HiddenInput

from tags.lib import tag_helpers
from groups.models import GroupProfile

class GroupForm(forms.ModelForm):

    class Meta:
        model = GroupProfile
        fields = ['groupname', 'privacy', 'membership', 'description', 'summary']

    def __init__(self, user=None, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        self.user = user

        if self.user: # user is only passed in on create
            formtype = "create"
        else:
            formtype = "update"
            self.fields['groupname'].widget = HiddenInput() # Can't edit groupname

        # Set tags
        self.fields = tag_helpers.add_tag_fields_to_form(
            self.fields, self.instance, formtype)

    def save(self, commit=True):
        instance = super(GroupForm, self).save(commit=False)

        if self.user:
            instance.owner = self.user
        instance.save()

        # Handle tags
        tags, form = tag_helpers.get_tags_from_valid_form(self)
        tag_helpers.add_tags_to_object(instance, tags)

        return instance