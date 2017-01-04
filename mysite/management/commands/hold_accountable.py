import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from commitments.models import Commitment


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            waiting_commitments = Commitment.objects.filter(status="waiting")
            for wc in waiting_commitments:
                wc.set_to_active_if_ready()
            print("Waiting commitments set to active")
            commitments = Commitment.objects.filter(status="active")
            for c in commitments:
                c.hold_accountable()
            print("People held accountable")
        except:
            raise CommandError("Failure holding people accountable")
