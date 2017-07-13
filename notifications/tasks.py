from django.contrib.auth.models import User
from django.db.models.signals import post_save
from notifications.lib import email_handlers

from mysite.constants import constants_table


def send_generic_emails(instance):
    if instance.status == "test":
        email_handlers.send_generic_email(constants_table["EMAIL_ADDRESS"], instance)
    if instance.status == "send":
        for user in User.objects.all():
            if not user.email:
                continue
            email_handlers.send_generic_email(user.email, instance)
