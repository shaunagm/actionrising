import datetime, ast
from django import forms
from django.utils import timezone

from commitments.models import Commitment

class CommitmentForm(forms.ModelForm):
    buddies = forms.MultipleChoiceField(required=False)

    class Meta:
        model = Commitment
        fields = ['buddies', 'offsite_buddies', 'message', 'tries', 'days_before_emailing']

    def __init__(self, user=None, action=None, *args, **kwargs):
        super(CommitmentForm, self).__init__(*args, **kwargs)
        if user:
            self.profile = user.profile
            self.action = action
        else:
            self.profile = self.instance.profile
            self.action = self.instance.action
        self.fields['buddies'].choices = [(i.pk, i) for i in self.profile.get_connected_people()]
        self.fields['buddies'].label = "Select friends on the site"
        self.fields['offsite_buddies'].label = "Add email addresses for friends off-site (5 max)"
        self.fields['message'].label = "Add an optional message for your friends."
        self.fields['tries'].label = "How many times should we email them?"
        self.fields['days_before_emailing'].label = "How many days should we wait before sending the first email?"

    def save(self, commit=True):
        instance = super(CommitmentForm, self).save(commit=False)
        instance.profile = self.profile
        instance.action = self.action
        days_wait = self.cleaned_data.get('days_before_emailing', 14)
        instance.update_start_date(days_wait)
        instance.save()
        return instance
