from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User

class Action(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    anonymize = models.BooleanField(default=False)
    main_link = models.CharField(max_length=300, blank=True, null=True)
    text = models.CharField(max_length=500, blank=True, null=True)  # Rich text?
    PRIVACY_CHOICES = (
        ('pub', 'Visible to Public'),
        ('sit', 'Visible Sitewide'),
        ('fol', 'Visible to Buddies and Those You Follow'),
        ('bud', 'Visible to Buddies'),
        ('you', 'Only Visible to You'),
        ('inh', 'Inherit'),
    )
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    # Inherit will need to be calculated each time, so we might want current_privacy generated from privacy
    location = models.CharField(max_length=140, blank=True, null=True)
    STATUS_CHOICES = (
        ('cre', 'In creation'),
        ('rea', 'Ready for action'),
        ('wit', 'Withdrawn'),
    )
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='cre')
    has_deadline = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)

    # Add get_status field which looks at has_deadline and returns either no deadline,
    # deadline not yet passed, or deadline passed.

    # Add get_privacy field which displays the privacy setting dependent on whether it's your
    # action, and what "inherit" is. (For now, it's just getting the field directly, which is not ideal.

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('action', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('edit_action', kwargs={'slug': self.slug})

    def get_action_creator_link(self):
        return reverse('profile', kwargs={'slug': self.creator.username})

class ActionTopic(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    text = models.CharField(max_length=200, blank=True, null=True)  # Rich text?
    actions = models.ManyToManyField(Action, blank=True, related_name="topics")

    def __unicode__(self):
        return self.name

    def get_link(self):
        return reverse('topic', kwargs={'slug': self.slug})

class ActionType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    text = models.CharField(max_length=200, blank=True, null=True)  # Rich text?
    actions = models.ManyToManyField(Action, blank=True, related_name="actiontypes")

    def __unicode__(self):
        return self.name

    def get_link(self):
        return reverse('type', kwargs={'slug': self.slug})
