"""
Signal listeners for Profile models
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from actions import location
from actions.models import District
from profiles.models import Profile

@receiver(post_save, sender=Profile)
def profile_post_save(instance, update_fields, created, **dummy):
    
    if created or (update_fields and 'location' in update_fields):
        location.populate_location_and_district(instance)