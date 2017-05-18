from __future__ import unicode_literals
from itertools import chain
import datetime, json

from actstream import action
from django.db.models.signals import post_save
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from ckeditor.fields import RichTextField
from mysite.settings import PRODUCTION_DOMAIN
from mysite.lib.choices import PrivacyChoices, PriorityChoices, StatusChoices, TimeChoices
from mysite.lib.privacy import privacy_tests
from mysite.lib.utils import disable_for_loaddata, slug_validator, slugify_helper
from profiles.lib.status_helpers import open_pars_when_action_reopens, close_pars_when_action_closes

DEFAULT_ACTION_DURATION = 60
DAYS_WARNING_BEFORE_CLOSURE = 3

class Action(models.Model):
    """ Stores a single action """

    # Basic action data
    slug = models.CharField(max_length=50, unique=True, validators=slug_validator)
    title = models.CharField(max_length=300)
    creator = models.ForeignKey(User)
    anonymize = models.BooleanField(default=False)
    main_link = models.CharField(max_length=300, blank=True, null=True)
    description = RichTextField(max_length=4000, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    duration = models.CharField(max_length=10, choices=TimeChoices.choices, default=TimeChoices.unknown)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.medium)

    # Privacy info
    privacy = models.CharField(max_length=10, choices=PrivacyChoices.choices, default=PrivacyChoices.inherit)
    current_privacy = models.CharField(max_length=10, choices=PrivacyChoices.choices, default=PrivacyChoices.sitewide)

    # Status info
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.ready)
    never_expires = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)
    close_date = models.DateTimeField(blank=True, null=True)

    # Related models
    flags = GenericRelation('flags.Flag')
    special_action = models.CharField(max_length=30, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        # If action is being created
        self.refresh_current_privacy()

        if self.pk:

            orig = Action.objects.get(pk=self.pk)
            if orig.status == StatusChoices.ready and self.status != StatusChoices.ready:
                close_pars_when_action_closes(self)
            if orig.status != StatusChoices.ready and self.status == StatusChoices.ready:
                open_pars_when_action_reopens(self)

            if self.deadline != orig.deadline or self.never_expires != orig.never_expires:
                self.set_close_date()

        else:
            self.slug = slugify_helper(Action, self.title)
            self.set_close_date()

        super(Action, self).save(*args, **kwargs)

    def get_cname(self):
        class_name = 'Action'
        return class_name

    def named(self):
        return not self.anonymize

    def get_creator(self):
        return self.creator

    def get_profile(self):
        return self.creator.profile

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

    def get_edit_url_with_domain(self):
        return PRODUCTION_DOMAIN + self.get_edit_url()

    def get_keep_open_url_with_domain(self):
        return PRODUCTION_DOMAIN + reverse('keep_open_action', kwargs={'pk': self.pk})

    def get_tags(self):
        return self.tags.all()

    def refresh_current_privacy(self):
        if self.privacy == PrivacyChoices.inherit:
            self.current_privacy = self.creator.profile.privacy_defaults.global_default
        else:
            self.current_privacy = self.privacy

    def get_visible_creator(self):
        if self.anonymize:
            return "Anonymous"
        else:
            return self.creator

    def is_active(self):
        if self.status == StatusChoices.ready:  # Arguably we should add 'in creation' too
            return True
        else:
            return False

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

    def set_close_date(self):
        if self.never_expires:
            self.close_date = None
        elif self.deadline:
            self.close_date = self.deadline
        else:
            self.close_date = self.date_created + datetime.timedelta(days=DEFAULT_ACTION_DURATION)

    def days_until(self, date):
        return (date - datetime.datetime.now(timezone.utc)).days

    def days_until_deadline(self):
        if self.deadline and not self.never_expires:
            return self.days_until(self.deadline)

    def close_action(self):
        if self.never_expires:
            return False
        if self.close_date and self.days_until(self.close_date) < 0:
            self.status = StatusChoices.finished
            self.save()
            return True
        return False

    def send_warning(self):
        if not self.deadline and (self.days_until(self.close_date) == DAYS_WARNING_BEFORE_CLOSURE):
            return True
        return False

    def keep_action_open(self):
        self.status = StatusChoices.ready
        self.close_date = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=DEFAULT_ACTION_DURATION)
        self.save()

    def is_visible_to(self, viewer, follows_user = None):
        return privacy_tests[self.current_privacy](self, viewer, follows_user)

@disable_for_loaddata
def action_handler(sender, instance, created, **kwargs):
    if not created and (timezone.now() - instance.date_created).seconds < 600:
        return  # Don't show updated if the action was created in the last ten minutes
    verb_to_use = "created" if created else "updated"
    # TODO: This is still going to be a problem if you change anonymity after creation,
    # we'll need to break some of the following links after anonymizing.
    if instance.named():
        action.send(instance.get_creator(), verb=verb_to_use, target=instance)
    else:
        action.send(instance, verb = 'was ' + verb_to_use)
post_save.connect(action_handler, sender=Action)

class ActionFilter(models.Model):
    creator = models.ForeignKey(User)
    saved = models.BooleanField(default=False) # If saved == false and created > 24 hrs old, delete
    date_created = models.DateTimeField(default=timezone.now)
    # Fields
    kinds = models.CharField(max_length=300, blank=True, null=True)
    topics = models.CharField(max_length=300, blank=True, null=True)
    time = models.CharField(max_length=300, blank=True, null=True)
    friends = models.BooleanField(default=False)
    plugin_fields = models.CharField(max_length=500, blank=True, null=True)

    def set_kinds(self, pks):
        self.kinds = json.dumps(pks)
        self.save()

    def get_kinds(self):
        if self.kinds:
            return json.loads(self.kinds)

    def get_kinds_string(self):
        # TODO: Fix naming issue, should be types rather than kinds
        # (See also wrong name in filterwizard_forms, but this needs a db migration)
        from tags.models import Tag
        kinds = Tag.objects.filter(kind="type").filter(id__in=self.get_kinds())
        return "Types of actions: " + ", ".join([tag.get_link_string() for tag in kinds])

    def set_topics(self, pks):
        self.topics = json.dumps(pks)
        self.save()

    def get_topics(self):
        if self.topics:
            return json.loads(self.topics)

    def get_topics_string(self):
        from tags.models import Tag
        topics = Tag.objects.filter(kind="topic").filter(id__in=self.get_topics())
        return "Topics of actions: " + ", ".join([tag.get_link_string() for tag in topics])

    def set_time(self, options):
        self.time = json.dumps(options)
        self.save()

    def get_time(self):
        if self.time:
            return json.loads(self.time)

    def get_time_string(self):
        display_names = [TimeChoices.labels[short] for short in self.get_time()]
        return "Duration of actions: " +  ", ".join(display_names)

    def get_plugin_fields(self):
        if self.plugin_fields:
            return json.loads(self.plugin_fields)

    def set_plugin_fields(self, data_dict):
        self.plugin_fields = json.dumps(data_dict)
        self.save()

    def get_plugin_field(self, fieldname):
        data_dict = self.get_plugin_fields()
        return data_dict[fieldname]

    def update_plugin_field(self, fieldname, fielddata):
        data_dict = self.get_plugin_fields()
        if not data_dict:
            data_dict = {}
        data_dict[fieldname] = fielddata
        self.set_plugin_fields(data_dict)

    def filter_actions(self):
        '''Runs filter and returns queryset'''
        current_queryset = Action.objects.all()
        if self.kinds:
            current_queryset = current_queryset.filter(tags__in=self.get_kinds())
        if self.topics:
            current_queryset = current_queryset.filter(tags__in=self.get_topics())
        if self.time:
            current_queryset = current_queryset.filter(duration__in=self.get_time())
        if self.friends:
            friend_ids = [user.id for user in self.creator.profile.get_people_tracking()]
            current_queryset = current_queryset.filter(creator__in=friend_ids)
        from plugins import plugin_helpers
        current_queryset = plugin_helpers.run_filters_for_plugins(self, current_queryset)
        return current_queryset

    def get_summary(self):
        strings = []
        if self.kinds:
            strings.append(self.get_kinds_string())
        if self.topics:
            strings.append(self.get_topics_string())
        if self.time:
            strings.append(self.get_time_string())
        if self.friends:
            strings.append("created by friends only")
        from plugins import plugin_helpers
        plugin_strings = plugin_helpers.get_plugin_field_strings(self)
        if plugin_strings:
            strings += plugin_strings
        return strings
