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
        # find lat / lng combo
        loc = location.geocode(instance.location)
        
        instance.lat = loc.latitude
        instance.lon = loc.longitude
        
        # find congressional District
        district = location.find_congressional_district(instance.lat, instance.lon)
        
        # use existing district if possible, otherwise create it
        local_district, created = District.objects.get_or_create(
            state=district['state'],
            district=district['district']
        )
        instance.district = local_district
        local_district.save()
        instance.save()