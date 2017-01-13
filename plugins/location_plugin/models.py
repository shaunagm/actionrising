from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Location(models.Model):

    location = models.CharField(max_length=140, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    district = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)

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
