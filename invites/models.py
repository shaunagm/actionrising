from __future__ import unicode_literals
import datetime, json, random, string

from django.utils import timezone
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from mysite.settings import NOTIFY_EMAIL, PRODUCTION_DOMAIN
from mysite.lib.utils import disable_for_loaddata
from notifications.lib.email_handlers import request_email

# Workflow

# 1: Person requests an account, automatically gets an email sent (unless they're flagged)
# as spam
# 2: User invites a friend, admin checks out "why" section, sends email to them
#    inviting them to fill out username, they fill it out, grants it to them, sends email.

def validate_email(email):
    user_email = User.objects.filter(email=email)
    if user_email:
        raise ValidationError("This email is already being used.")

def validate_username(username):
    user_name = User.objects.filter(username=username)
    if user_name:
        raise ValidationError("This username is already taken.")

class Invite(models.Model):
    username = models.CharField(max_length=50, blank=True, null=True, validators=[validate_username])
    email = models.CharField(max_length=50, unique=True, validators=[validate_email])
    reasoning = models.CharField(max_length=1000, blank=True, null=True)
    message = models.CharField(max_length=500, blank=True, null=True)
    self_submitted = models.BooleanField(default=False)
    REQUEST_CHOICES = (
        ('submitted', _('Request submitted')),
        ('approved', _('Request approved by admin')),
        ('emailed', _('Confirmation email sent')),
        ('done', _('User has joined site')),
        ('duplicate', _('User already on site')),
    )
    request_status = models.CharField(max_length=10, choices=REQUEST_CHOICES, default='submitted')
    invited_by = models.CharField(max_length=500, blank=True, null=True)
    initial_request_date = models.DateTimeField(default=timezone.now)
    confirmation_url_string = models.CharField(max_length=30, blank=True)
    requester_hash = models.CharField(max_length=40, blank=True)

    def __unicode__(self):
        return u'Invite for %s' % (self.email)

    def save(self, *args, **kwargs):
        if not self.confirmation_url_string:
            self.confirmation_url_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
        if self.request_status == "submitted" and self.self_submitted:
            request_email(self)
            self.request_status = "emailed"
        super(Invite, self).save(*args, **kwargs)

    def get_confirmation_url(self):
        if self.self_submitted:
            return PRODUCTION_DOMAIN + reverse('sign-up-confirmation', kwargs={'slug': self.confirmation_url_string })
        else:
            return PRODUCTION_DOMAIN + reverse('invite-confirmation', kwargs={'slug': self.confirmation_url_string })

    def get_inviters(self):
        if self.invited_by is not None:
            return json.loads(self.invited_by)
        return []

    def get_inviter_string(self):
        return (", ").join(self.get_inviters())

    def set_inviters(self, inviters):
        self.invited_by = json.dumps(inviters)
        self.save()

    def add_inviter(self, inviter):
        inviters = self.get_inviters()
        if inviter not in inviters:
            inviters.append(inviter)
        self.set_inviters(inviters)

    def string_representation(self):
        return "Username: %s, Email: %s, Reasoning: %s, Message: %s, Status: %s" % (self.username,
            self.email, self.reasoning, self.message, self.request_status)
