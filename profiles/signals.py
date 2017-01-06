"""
Signal listeners for Profile models
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from actions.lib import act_location
from profiles.models import Profile

@receiver(post_save, sender=Profile)
def profile_post_save(instance, update_fields, created, **dummy):

    if created or (update_fields and 'location' in update_fields):
        act_location.populate_location_and_district(instance)
