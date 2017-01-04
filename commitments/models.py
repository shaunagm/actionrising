from __future__ import unicode_literals

import json, ast
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save

from django.contrib.auth.models import User
from actions.models import Action
from profiles.models import Profile, ProfileActionRelationship
from notifications.lib import email_handlers
from mysite.lib.choices import COMMITMENT_STATUS_CHOICES
from mysite.lib.utils import disable_for_loaddata

class Commitment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=COMMITMENT_STATUS_CHOICES,
        default='waiting')
    buddies = models.CharField(max_length=400, blank=True, null=True) # Add getters + setters to store this in json
    offsite_buddies = models.CharField(max_length=400, blank=True, null=True) # Add getters + setters to store this in json
    message = models.CharField(max_length=400, blank=True, null=True)
    start_emails = models.DateField(default=timezone.now)
    tries = models.IntegerField(default=3)

    def __unicode__(self):
        return u'Commitment of profile %s to action %s' % (self.profile, self.action)

    def days_past_start(self):
        return (datetime.datetime.today() - self.start_emails).days

    def days_given(self):
        '''The number of days past the start of emails we give until expiration.'''
        grace_days = 30
        return (tries * 7) + grace_days

    def reopen(self):
        if datetime.datetime.today() < self.start_emails:
            self.status = "waiting"
            self.save()
            return
        if self.days_past_start() < self.days_given():
            self.status = "active"
        else:
            self.status = "expired"
        self.save()

    def set_to_active_if_ready(self):
        if datetime.datetime.now() < self.start_emails:
            self.status = "active"
            self.save()

    def calculate_notification_dates(self):
        dates = []
        for count, t in enumerate(tries, 1):
            dates.append(self.start_emails + timedelta(days=7*count))
        return dates

    def hold_accountable_if_time(self):
        if self.days_past_start() < self.days_given():
            if datetime.datetime.today() in self.calculate_notification_dates():
                self.hold_accountable()
        else:
            self.status = "expired"
            self.save()

    def collect_emails(self):
        emails = []
        for b in ast.literal_eval(self.buddies):
            buddy = Profile.objects.get(pk=int(b))
            if buddy.user.email:
                emails.append({ 'email': None, 'user': buddy })
        for ob in self.get_offsite_buddies():
            emails.append({ 'email': ob, 'user': None })
        return emails

    def hold_accountable(self):
        emails = self.collect_emails()
        for email in emails:
            if email['user']:
                email_handlers.hold_accountable_email(email['user'], self)
            elif email['email']:
                email_handlers.hold_accountable_email_nonuser(email['email'], self)

    def get_offsite_buddies(self):
        if self.offsite_buddies:
            email_string = self.offsite_buddies.strip("[]")
            return email_string.split(",")
        return []
