from django.db.models.signals import post_save
from django.dispatch import receiver
from profiles.models import Profile
from plugins.location_plugin.models import Location
from django.contrib.contenttypes.models import ContentType

@receiver(post_save, sender=Profile)
def my_handler(sender, instance, created, **kwargs):
    if created:
        ctype = ContentType.objects.get_for_model(sender)
        location = Location.objects.create(content_type=ctype, object_id=instance.pk)
