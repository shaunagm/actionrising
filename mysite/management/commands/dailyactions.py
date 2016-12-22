from django.core.management.base import BaseCommand, CommandError

from notifications.lib.notification_handlers import send_daily_actions

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            send_daily_actions()
            print("Daily actions sent")
        except:
            raise CommandError("Failure running daily actions")
