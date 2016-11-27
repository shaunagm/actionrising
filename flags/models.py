from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.utils import timezone
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User

class Flag(models.Model):
    """Stores a flag model that can be applied to actions, slates and other objects"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    flagged_by = models.ForeignKey(User)
    date_created = models.DateTimeField(default=timezone.now)
    FLAG_CHOICES = (
        ('spam', _('I believe that this is spam')),
        ('abuse', _('I believe that this is abusive or harassing')),
        ('wrong', _('I believe that this is inaccurate')),
        ('other', _('I am flagging this for other reasons')),
    )
    flag_choice = models.CharField(max_length=5, choices=FLAG_CHOICES, default='other')
    FLAG_STATUS_CHOICES = (
        ('new', _('New flag')),
        ('reject', _('Flag was rejected as invalid')),
        ('approve', _('Flag was approved as valid')),
        ('discuss', _('Flag needs further investigation')),
    )
    flag_status = models.CharField(max_length=10, choices=FLAG_STATUS_CHOICES, default='new')

    def __unicode__(self):
        return "%s flagged by %s as %s" % (self.content_object.title, self.flagged_by.username, self.flag_choice)
