from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from plugins.location_plugin.lib import locations
from mysite.lib.utils import disable_for_loaddata

class Location(models.Model):

    location = models.CharField(max_length=140, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    district = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    hide_location = models.BooleanField(default=False)

    # Related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "Location of %s" % self.content_object

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

@disable_for_loaddata
def location_post_save(instance, update_fields, created, **dummy):
    # We don't need to specify which update_field, because "location" should be
    # the only thing ever updated by the user.
    post_save.disconnect(location_post_save, sender=Location) # Prevents recursion
    locations.populate_location_and_district(instance)
    post_save.connect(location_post_save, sender=Location) # Reconnect
post_save.connect(location_post_save, sender=Location)

def get_objects_given_location(location, include=["State", "District", "National"]):
    if "District" in include:
        q_object = Q(district=location.district)
    if "State" in include:
        try:
            q_object.add(Q(state=location.state), Q.OR)
        except:
            q_object = Q(state=location.state)
    if "National" in include:
        try:
            q_object.add(Q(state=None), Q.OR)
        except:
            q_object = Q(state=None)
    return Location.objects.filter(q_object)

def get_actions_given_location(location, include=["State", "District", "National"]):
    from actions.models import Action
    locations = get_objects_given_location(location, include)
    actions = []
    for location in locations:
        if location.content_type.model_class() == Action:
            actions.append(location)
    return actions

def filter_queryset_by_location(field_data, queryset, user):
    # If none selected, no filtering to be done
    if not field_data:
        return queryset
    # If "get everything" selected, no filtering to be done
    if 'Everything' in field_data:
        return queryset
    # If user has no location, no filtering to be done
    ctype = ContentType.objects.get_for_model(user.profile)
    location = Location.objects.filter(content_type=ctype, object_id=user.profile.pk).first()
    if not location or location.location in ["", None]:
        return queryset
    # Okay, filter time!
    actions = get_actions_given_location(location, field_data)
    action_ids = [action.id for action in actions]
    return results.filter(id__in=action_ids)
