from __future__ import unicode_literals
from itertools import chain
import datetime

from actstream import action
from django.db.models.signals import post_save
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from ckeditor.fields import RichTextField
from mysite.settings import PRODUCTION_DOMAIN
from mysite.lib.choices import (PRIVACY_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES,
    TIME_CHOICES, INDIVIDUAL_STATUS_CHOICES)
from mysite.lib.utils import disable_for_loaddata, slug_validator, slugify_helper
from profiles.lib.status_helpers import open_pars_when_action_reopens, close_pars_when_action_closes

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
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    district = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    # status default is rea == open for action
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='rea')
    has_deadline = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)
    # suggested priority default is med == medium
    priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default='med')
    date_created = models.DateTimeField(default=timezone.now)
    flags = GenericRelation('flags.Flag')
    # default default is H == 'Unknown or variable'
    duration = models.CharField(max_length=2, choices=TIME_CHOICES, default='H')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If action is being created
        if not self.pk:
            self.slug = slugify_helper(Action, self.title)
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        if self.privacy != "inh" and self.privacy != self.current_privacy:
            self.current_privacy = self.privacy
        if self.pk:
            orig = Action.objects.get(pk=self.pk)
            if orig.status == "rea" and self.status != "rea":
                close_pars_when_action_closes(self)
            if orig.status != "rea" and self.status == "rea":
                open_pars_when_action_reopens(self)
        super(Action, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'Action'
        return class_name

    def get_absolute_url(self):
        return reverse('action', kwargs={'slug': self.slug})

    def get_absolute_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_absolute_url()

    def get_mark_as_done_url_with_domain(self):
        return PRODUCTION_DOMAIN + reverse('mark_as_done',
            kwargs={'slug': self.slug, 'mark_as': 'done'})

    def get_robust_url(self):
        try:
            url = reverse('action', kwargs={'slug': self.slug})
            return url
        except:
            return ""

    def get_edit_url(self):
        return reverse('edit_action', kwargs={'slug': self.slug})

    def get_tags(self):
        return self.action_tags.all()

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

    def get_district(self):
        if self.district:
            return self.district
        return None

    def get_state(self):
        if self.state:
            return self.state
        return None

    def get_district_and_state(self):
        return "%s, %s" % (self.district, self.state)

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
