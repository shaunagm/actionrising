from django.core.management.base import BaseCommand, CommandError
from actions.models import Action
from notifications.lib import email_handlers
from mysite.lib.choices import StatusChoices

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            actions = Action.objects.filter(status=StatusChoices.ready)
            for action in actions:
                closed = action.close_action()
                email_handlers.close_action_emails(action, closed)
            print("Actions marked as finished")
        except:
            raise CommandError("Failure marking actions as finished")
