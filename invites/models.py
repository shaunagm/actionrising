from __future__ import unicode_literals
import datetime, json, random, string

from django.utils import timezone
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from mysite.settings import NOTIFY_EMAIL, PRODUCTION_DOMAIN
from mysite.utils import disable_for_loaddata
from notifications.email_templates import generate_invite_notification_email

# Workflow

# 1: Person requests an invite, admin checks out "why" section, grants it to them, sends
#    email.
# 2: User invites a friend, admin checks out "why" section, sends email to them
#    inviting them to fill out username, they fill it out, grants it to them, sends email.

class Invite(models.Model):
    username = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, unique=True)
    reasoning = RichTextField(max_length=1000, blank=True, null=True)
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
        if self.pk:
            orig = Invite.objects.get(pk=self.pk)
            if orig.request_status == "submitted" and self.request_status == "approved":
                if orig.self_submitted:
                    self.send_invite_email("self")
                else:
                    self.send_invite_email("invited")
                self.request_status = "emailed"
        if not self.confirmation_url_string:
            self.confirmation_url_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
        super(Invite, self).save(*args, **kwargs)

    def get_confirmation_url(self):
        if self.self_submitted:
            return PRODUCTION_DOMAIN + reverse('request-confirmation', kwargs={'slug': self.confirmation_url_string })
        else:
            return PRODUCTION_DOMAIN + reverse('invite-confirmation', kwargs={'slug': self.confirmation_url_string })

    def send_invite_email(self, kind):
        email_subj, email_message, html_message = generate_invite_notification_email(kind, self)
        sent = send_mail(email_subj, email_message, NOTIFY_EMAIL, [self.email],
            fail_silently=False, html_message=html_message)

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

@disable_for_loaddata
def invite_email_handler(sender, instance, created, **kwargs):
    if created:
        email_subj = "There's been an invite requested on ActionRising"
        message = "https://www.actionrising.com/admin/invites/invite/" + str(instance.pk)
        html_message = "<a href='https://www.actionrising.com/admin/invites/invite/" + str(instance.pk) + "/change'>Click here</a>"
        sent = send_mail(email_subj, message, NOTIFY_EMAIL, ['actionrisingsite@gmail.com'],
            fail_silently=False, html_message=html_message)
post_save.connect(invite_email_handler, sender=Invite)
