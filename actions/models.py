from __future__ import unicode_literals
from itertools import chain
import re

from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User

from mysite.utils import PRIVACY_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES, check_privacy

slug_validator = [
    RegexValidator(
        regex=re.compile(r"^[a-z0-9-]+$"),
        message="Please enter a valid slug, using only lowercase letters, numbers, and dashes.",
        code="invalid"
    )
]

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
    slug = models.CharField(max_length=50, unique=True, validators=slug_validator)
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

    def get_cname(self):
        class_name = 'Action'
        return class_name

    def get_absolute_url(self):
        return reverse('action', kwargs={'slug': self.slug})

    def get_robust_url(self):
        try:
            url = reverse('action', kwargs={'slug': self.slug})
            return url
        else:
            return ""

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

    def get_slates(self, user):
        anonymous_count = 0
        public_list = []
        for slate in self.slate_set.all():
            sar = slate.get_sar_given_action(self)
            if check_privacy(sar, user):
                public_list.append(slate)
            else:
                anonymous_count += 1
        return {'anonymous_count': anonymous_count, 'total_count': anonymous_count + len(public_list),
            'public_list': public_list }

    def get_trackers(self, user):
        anonymous_count = 0
        public_list = []
        for person in self.profile_set.all():
            par = person.get_par_given_action(self)
            if check_privacy(par, user):
                public_list.append(person)
            else:
                anonymous_count += 1
        return {'anonymous_count': anonymous_count, 'total_count': anonymous_count + len(public_list),
            'public_list': public_list }

class Slate(models.Model):
    slug = models.CharField(max_length=50, unique=True, validators=slug_validator)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    text = models.CharField(max_length=200, blank=True, null=True)  # Rich text?
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='cre')
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    actions = models.ManyToManyField(Action, through='SlateActionRelationship')

    def __unicode__(self):
        return self.slug

    def get_cname(self):
        class_name = 'Slate'
        return class_name

    def get_absolute_url(self):
        return reverse('slate', kwargs={'slug': self.slug})

    def get_robust_url(self):
        try:
            url = reverse('slate', kwargs={'slug': self.slug})
            return url
        else:
            return ""

    def get_edit_url(self):
        return reverse('edit_slate', kwargs={'slug': self.slug})

    def get_sar_given_action(self, action):
        try:
            return SlateActionRelationship.objects.get(slate=self, action=action)
        except:
            return None

class SlateActionRelationship(models.Model):
    slate = models.ForeignKey(Slate, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')

    def get_cname(self):
        class_name = 'SlateActionRelationship'
        return class_name

    def __unicode__(self):
        return "Relationship of slate: %s and action: %s " % (self.slate, self.action)
