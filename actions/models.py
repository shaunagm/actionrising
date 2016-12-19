from __future__ import unicode_literals
from itertools import chain
import re, datetime

from actstream import action
from django.db.models.signals import post_save
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from ckeditor.fields import RichTextField
from mysite.settings import PRODUCTION_DOMAIN

from mysite.utils import (PRIVACY_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES,
    TIME_CHOICES, INDIVIDUAL_STATUS_CHOICES, disable_for_loaddata)

slug_validator = [
    RegexValidator(
        regex=re.compile(r"^[a-z0-9-]+$"),
        message="Enter a slug, using only lowercase letters, numbers, and dashes.",
        code="invalid"
    )
]

def slugify_helper(object_model, slug):
    counter = 0
    temp_slug = slugify(slug)[:45]
    while True:
        if object_model.objects.filter(slug=temp_slug):
            temp_slug += str(counter)
            counter += 1
            continue
        break
    return temp_slug

class ActionTopic(models.Model):
    """Stores the topic (name, slug, and description) of an action"""
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)  # TODO Rich text?

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify_helper(ActionTopic, self.name)
        super(ActionTopic, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'ActionTopic'
        return class_name

    def get_link(self):
        return reverse('topic', kwargs={'slug': self.slug})

    def action_count(self):
        return self.actions_for_topic.count()

class ActionType(models.Model):
    """Stores the type (name, slug, and description) of an action"""
    name = models.CharField(max_length=40, unique=True)
    slug = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)  # TODO Rich text?

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify_helper(ActionType, self.name)
        super(ActionType, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'ActionType'
        return class_name

    def get_link(self):
        return reverse('type', kwargs={'slug': self.slug})

    def action_count(self):
        return self.actions_for_type.count()

class Action(models.Model):
    """ Stores a single action """
    slug = models.CharField(max_length=50, unique=True, validators=slug_validator)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    anonymize = models.BooleanField(default=False)
    main_link = models.CharField(max_length=300, blank=True, null=True)
    description = RichTextField(max_length=2500, blank=True, null=True)  # TODO Rich text?
    # privacy default is inh == inherit
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    current_privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='sit')
    location = models.CharField(max_length=140, blank=True, null=True)
    # status default is rea == open for action
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='rea')
    has_deadline = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)
    # suggested priority default is med == medium
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    actiontypes = models.ManyToManyField(ActionType, blank=True, related_name="actions_for_type")
    topics = models.ManyToManyField(ActionTopic, blank=True, related_name="actions_for_topic")
    date_created = models.DateTimeField(default=timezone.now)
    flags = GenericRelation('flags.Flag')
    # default default is H == 'Unknown or variable'
    duration = models.CharField(max_length=2, choices=TIME_CHOICES, default='H')

    # TODO Add get_status field
    #      which looks at has_deadline and returns either no deadline,
    #      deadline not yet passed, or deadline passed.

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify_helper(Action, self.title)
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        if self.privacy != "inh" and self.privacy != self.current_privacy:
            self.current_privacy = self.privacy
        super(Action, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'Action'
        return class_name

    def get_absolute_url(self):
        return reverse('action', kwargs={'slug': self.slug})

    def get_absolute_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_absolute_url()

    def get_robust_url(self):
        try:
            url = reverse('action', kwargs={'slug': self.slug})
            return url
        except:
            return ""

    def get_edit_url(self):
        return reverse('edit_action', kwargs={'slug': self.slug})

    def get_action_creator_link(self):
        return reverse('profile', kwargs={'pk': self.creator.pk})

    def get_tags(self):
        return list(chain(self.topics.all(), self.actiontypes.all()))

    def refresh_current_privacy(self):
        if self.privacy == "inh":
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        else:
            self.current_privacy = self.privacy
        self.save()

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

    def is_active(self):
        if self.status == "rea":  # Arguably we should add 'in creation' too
            return True
        else:
            return False

    def get_location(self):
        if self.location:
            return self.location
        else:
            return "Unknown"

    def get_status(self):
        # Added for conveniences' sake in vet_actions function
        return self.get_status_display()

    def get_days_til_deadline(self):
        now = datetime.datetime.now(timezone.utc)
        if (self.deadline) and (self.deadline > now):
            days = (self.deadline - now).days
            if days > 0:
                return days
            else:
                return float((self.deadline - now).seconds)/float(86400)
        return -1

    def is_flagged_by_user(self, user, new_only=False):
        for flag in self.flags.all():
            if flag.flagged_by == user:
                if new_only:
                    return flag if flag.flag_status == "new" else "No flags"
                else:
                    return flag
        return "No flags"

@disable_for_loaddata
def action_handler(sender, instance, created, **kwargs):
    if not created and (timezone.now() - instance.date_created).seconds < 600:
        return  # Don't show updated if the action was created in the last ten minutes
    verb_to_use = "created" if created else "updated"
    if instance.get_creator() == "Anonymous":
        # TODO: This is still going to be a problem if you change anonymity after creation,
        # we'll need to break some of the following links after anonymizing.
        action.send(instance, verb="was "+verb_to_use)
    else:
        action.send(instance.creator, verb=verb_to_use, target=instance)
post_save.connect(action_handler, sender=Action)


class Slate(models.Model):
    """Stores a single slate."""
    slug = models.CharField(max_length=50, unique=True, validators=slug_validator)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    description = RichTextField(max_length=2500, blank=True, null=True)  # TODO Rich text?
    # status default is rea == open for action
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='rea')
    # default privacy is inh == inherit
    privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='inh')
    current_privacy = models.CharField(max_length=3, choices=PRIVACY_CHOICES, default='sit')
    actions = models.ManyToManyField(Action, through='SlateActionRelationship')
    date_created = models.DateTimeField(default=timezone.now)
    flags = GenericRelation('flags.Flag')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify_helper(Slate, self.title)
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        else:
            if self.privacy != "inh" and self.privacy != self.current_privacy:
                self.current_privacy = self.privacy
        super(Slate, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'Slate'
        return class_name

    def get_absolute_url(self):
        return reverse('slate', kwargs={'slug': self.slug})

    def get_absolute_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_absolute_url()

    def get_robust_url(self):
        try:
            url = reverse('slate', kwargs={'slug': self.slug})
            return url
        except:
            return ""

    def get_edit_url(self):
        return reverse('edit_slate', kwargs={'slug': self.slug})

    # TODO rename method?
    def get_sar_given_action(self, action):
        """Return SlateActionRelationship for a specific action"""
        try:
            return SlateActionRelationship.objects.get(slate=self, action=action)
        except:
            return None

    def is_active(self):
        if self.status == "rea":  # Arguably we should add 'in creation' too
            return True
        else:
            return False

    def is_flagged_by_user(self, user, new_only=False):
        for flag in self.flags.all():
            if flag.flagged_by == user:
                if new_only:
                    return flag if flag.flag_status == "new" else "No flags"
                else:
                    return flag
        return "No flags"

    def refresh_current_privacy(self):
        if self.privacy == "inh":
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        else:
            self.current_privacy = self.privacy
        self.save()

@disable_for_loaddata
def slate_handler(sender, instance, created, **kwargs):
    if not created and (timezone.now() - instance.date_created).seconds < 600:
        return  # Don't show updated if the slate was created in the last ten minutes
    if created:
        action.send(instance.creator, verb='created', target=instance)
    else:
        # TODO: Check if only the associated actions changed, and if so squash this
        action.send(instance.creator, verb='updated', target=instance)
post_save.connect(slate_handler, sender=Slate)

class SlateActionRelationship(models.Model):
    """Stores relationship between a single slate and a single action."""
    slate = models.ForeignKey(Slate, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    # default priority is med == medium
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    # default status is ace == accepted
    status = models.CharField(max_length=3, choices=INDIVIDUAL_STATUS_CHOICES, default='ace')
    notes = models.CharField(max_length=2500, blank=True, null=True)

    def get_cname(self):
        class_name = 'SlateActionRelationship'
        return class_name

    def __unicode__(self):
        return "Relationship of slate: %s and action: %s " % (self.slate, self.action)

    def get_status(self):
        if self.action.status in ["wit", "rej"]:
            return self.action.get_status_display()
        else:
            return self.get_status_display()

@disable_for_loaddata
def sar_handler(sender, instance, created, **kwargs):
    if created:
        action.send(instance.slate.creator, verb="added", action_object=instance.action, target=instance.slate)
post_save.connect(sar_handler, sender=SlateActionRelationship)
