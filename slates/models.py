from __future__ import unicode_literals

from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from actstream import action
from ckeditor.fields import RichTextField

from actions.models import Action
from mysite.settings import PRODUCTION_DOMAIN
from mysite.lib import choices
from mysite.lib.utils import disable_for_loaddata, slug_validator, slugify_helper
from profiles.lib.status_helpers import open_pars_when_action_reopens, close_pars_when_action_closes


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

    def refresh_current_privacy(self):
        if self.privacy == "inh":
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        else:
            self.current_privacy = self.privacy
        self.save()

    def get_people_to_notify(self):
        people = []
        for psr in self.profileslaterelationship_set.all():
            if psr.notify_of_additions:
                people.append(psr.profile.user)
        return people

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
