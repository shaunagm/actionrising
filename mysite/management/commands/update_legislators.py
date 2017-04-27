from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

from sunlight.services.congress import Congress

from plugins.phonescript_plugin.models import Legislator

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            # query sunlight API
            congress_api = Congress(use_https=False)
            leg_dict = {}
            legislators = congress_api.legislators(per_page="all")
            # get new legislators
            for leg in legislators:
                leg_object = Legislator.objects.filter(bioguide_id=leg['bioguide_id'])
                if not leg_object:
                    Legislator.objects.create(bioguide_id=leg['bioguide_id'],
                        first_name=leg['first_name'], last_name=leg['last_name'],
                        title=leg['title'], phone=leg['phone'], state=leg['state'],
                        district=leg['district'], party=leg['party'])
            # retire old legislators
            ids = [leg['bioguide_id'] for leg in legislators]
            for leg_object in Legislator.objects.all():
                if leg_object.bioguide_id not in ids:
                    leg_object.in_office = False
                    leg_object.save()
            # update cache
            district_selects = [leg.select_name() for leg
                in Legislator.objects.filter(district__isnull=False, in_office=True).order_by('state', 'district')]
            cache.set('district_selects', district_selects, 1209600) # Expiration set to two weeks
            print("Legislator cache updated")
        except:
            raise CommandError("Failure updating legislator cache")
