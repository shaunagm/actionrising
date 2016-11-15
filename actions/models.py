from __future__ import unicode_literals
from itertools import chain

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User

from mysite.utils import PRIVACY_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES

class ActionTopic(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    text = models.CharField(max_length=200, blank=True, null=True)  # Rich text?

    def __unicode__(self):
        return self.name

    def get_cname(self):
        class_name = 'ActionTopic'
        return class_name

    def get_link(self):
        return reverse('topic', kwargs={'slug': self.slug})

class ActionType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    text = models.CharField(max_length=200, blank=True, null=True)  # Rich text?

    def __unicode__(self):
        return self.name

    def get_cname(self):
        class_name = 'ActionType'
        return class_name

    def get_link(self):
        return reverse('type', kwargs={'slug': self.slug})

class Action(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    anonymize = models.BooleanField(default=False)
    main_link = models.CharField(max_length=300, blank=True, null=True)
    text = models.CharField(max_length=500, blank=True, null=True)  # Rich text?
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    location = models.CharField(max_length=140, blank=True, null=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='cre')
    has_deadline = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)
    suggested_priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    actiontypes = models.ManyToManyField(ActionType, blank=True, related_name="actions_for_type")
    topics = models.ManyToManyField(ActionTopic, blank=True, related_name="actions_for_topic")

    # Add get_status field which looks at has_deadline and returns either no deadline,
    # deadline not yet passed, or deadline passed.

    # Add get_privacy field which displays the privacy setting dependent on whether it's your
    # action, and what "inherit" is. (For now, it's just getting the field directly, which is not ideal.
    # Inherit will need to be calculated each time, so we might want current_privacy generated from privacy

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('action', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('edit_action', kwargs={'slug': self.slug})

    def get_action_creator_link(self):
        return reverse('profile', kwargs={'slug': self.creator.username})

    def get_tags(self):
        return list(chain(self.topics.all(), self.actiontypes.all()))

    def get_creator(self):
        if self.anonymize:
            return "Anonymous"
        else:
            return self.creator

    def get_creator_with_link(self):
        if self.anonymize:
            return "Anonymous"
        else:
            return "<a href='" + self.get_action_creator_link() + "'>" + self.creator.username + "</a>"

class Slate(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    text = models.CharField(max_length=200, blank=True, null=True)  # Rich text?
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='cre')
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    actions = models.ManyToManyField(Action, through='SlateActionRelationship')

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('slate', kwargs={'slug': self.slug})

class SlateActionRelationship(models.Model):
    slate = models.ForeignKey(Slate, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
