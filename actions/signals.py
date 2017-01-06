"""
Signal listeners for Action models
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from actions.lib import act_location
from actions.models import Action


@receiver(post_save, sender=Action)
def action_post_save(instance, update_fields, created, **dummy):

    if created or (update_fields and 'location' in update_fields):
        act_location.populate_location_and_district(instance)
