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
