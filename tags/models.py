from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _

from actions.models import Action
from slates.models import Slate
from profiles.models import Profile

TAG_CHOICES = (
    ('topic', _('Topic')),
    ('type', _('Type')),
    ('goal', _('Goal')),
)

class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)  # TODO Rich text?
    kind = models.CharField(max_length=10, choices=TAG_CHOICES, default='topic')
    # Related objects
    actions = models.ManyToManyField(Action, blank=True, related_name="action_tags")
    slates = models.ManyToManyField(Slate, blank=True, related_name="slate_tags")
    profiles = models.ManyToManyField(Profile, blank=True, related_name="profile_tags")

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.kind)
