from __future__ import unicode_literals

from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from actstream import action
from ckeditor.fields import RichTextField

from mysite.lib.choices import (PrivacyChoices, PriorityChoices, StatusChoices,
    ToDoStatusChoices)
from actions.models import Action
from mysite.settings import PRODUCTION_DOMAIN
from mysite.lib import choices
from mysite.lib.privacy import privacy_tests
from mysite.lib.utils import disable_for_loaddata, slug_validator, slugify_helper

class Slate(models.Model):
    """Stores a single slate."""
    slug = models.CharField(max_length=50, unique=True, validators=slug_validator)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    description = RichTextField(max_length=2500, blank=True, null=True)  # TODO Rich text?
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.ready)
    privacy = models.CharField(max_length=10, choices=PrivacyChoices.choices, default=PrivacyChoices.inherit)
    current_privacy = models.CharField(max_length=10, choices=PrivacyChoices.choices, default=PrivacyChoices.sitewide)
    actions = models.ManyToManyField(Action, through='SlateActionRelationship')
    date_created = models.DateTimeField(default=timezone.now)
    flags = GenericRelation('flags.Flag')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify_helper(Slate, self.title)

        self.refresh_current_privacy()
        super(Slate, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'Slate'
        return class_name

    def named(self):
        return True

    def get_creator(self):
        return self.creator

    def get_profile(self):
        return self.creator.profile

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
        if self.status == StatusChoices.ready:  # Arguably we should add 'in creation' too
            return True
        else:
            return False

    def refresh_current_privacy(self):
        if self.privacy == PrivacyChoices.inherit:
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        else:
            self.current_privacy = self.privacy

    def get_people_to_notify(self):
        people = []
        for psr in self.profileslaterelationship_set.all():
            if psr.notify_of_additions:
                people.append(psr.profile.user)
        return people

    def is_visible_to(self, viewer, follows_user = None):
        return privacy_tests[self.current_privacy](self, viewer, follows_user)

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
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.medium)
    status = models.CharField(max_length=10, choices=ToDoStatusChoices.choices, default=ToDoStatusChoices.accepted)
    notes = models.CharField(max_length=2500, blank=True, null=True)

    def get_cname(self):
        class_name = 'SlateActionRelationship'
        return class_name

    def get_creator(self):
        return self.slate.get_creator()

    def get_profile(self):
        return self.slate.get_creator().profile

    def __unicode__(self):
        return "Relationship of slate: %s and action: %s " % (self.slate, self.action)

    def named(self):
        return self.action.named()

    def get_status(self):
        if self.action.status is ToDoStatusChoices.rejected:
            return self.action.get_status_display()
        else:
            return self.get_status_display()

    def is_visible_to(self, viewer, follows_user = None):
        return self.action.is_visible_to(viewer, follows_user) and self.slate.is_visible_to(viewer, follows_user)

@disable_for_loaddata
def sar_handler(sender, instance, created, **kwargs):
    if created:
        action.send(instance.slate.creator, verb="added", action_object=instance.action, target=instance.slate)
post_save.connect(sar_handler, sender=SlateActionRelationship)
