from __future__ import unicode_literals

import json, ast, datetime, pytz
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
    start_emails = models.DateTimeField(default=timezone.now)
    tries = models.IntegerField(default=3)
    days_before_emailing = models.IntegerField(default=14)

    def __unicode__(self):
        return u'Commitment of profile %s to action %s' % (self.profile, self.action)

    def update_start_date(self, days_wait):
        if not self.pk:
            self.start_emails = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=days_wait)
        else:
            orig = Commitment.objects.get(pk=self.pk)
            if orig.days_before_emailing != days_wait:
                diff = days_wait - orig.days_before_emailing
                self.start_emails = self.start_emails + datetime.timedelta(days=diff)

    def days_past_start(self):
        return (datetime.datetime.now(tz=pytz.utc) - self.start_emails).days

    def days_given(self):
        '''The number of days past the start of emails we give until expiration.'''
        grace_days = 30
        return (self.tries * 7) + grace_days

    def reopen(self):
        if self.days_past_start() < 0:
            self.status = "waiting"
            self.save()
            return
        if self.days_past_start() < self.days_given():
            self.status = "active"
        else:
            self.status = "expired"
        self.save()

    def set_to_active_if_ready(self):
        if self.days_past_start() >= 0:
            self.status = "active"
            self.save()

    def calculate_notification_dates(self):
        dates = []
        for t in range(1, self.tries+1):
            new_dt = self.start_emails + datetime.timedelta(days=7*t)
            dates.append(new_dt.date())
        return dates

    def get_buddies(self):
        if self.buddies:
            buddies = ast.literal_eval(self.buddies)
            return list(Profile.objects.filter(pk__in=[int(b) for b in buddies]))
        return []

    def get_offsite_buddies(self):
        if self.offsite_buddies:
            email_string = self.offsite_buddies.strip("[]")
            return email_string.split(",")
        return []

    def collect_buddy_info(self):
        info = []
        for b in self.get_buddies():
            if b.user.email:
                info.append({ 'email': None, 'user': b })
        for ob in self.get_offsite_buddies():
            info.append({ 'email': ob, 'user': None })
        return info

    def hold_accountable(self):
        buddy_info = self.collect_buddy_info()
        for buddy in buddy_info:
            if buddy['user']:
                email_handlers.hold_accountable_email(buddy['user'], self)
            elif buddy['email']:
                email_handlers.hold_accountable_email_nonuser(buddy['email'], self)

    def hold_accountable_if_time(self):
        if self.days_past_start() < self.days_given():
            if datetime.date.today() in self.calculate_notification_dates():
                self.hold_accountable()
        else:
            self.status = "expired"
            self.save()
