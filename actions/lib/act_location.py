import sys
from actions.models import Action, District
from geopy.exc import GeopyError
from geopy.geocoders import GoogleV3
from sunlight.services.congress import Congress
from sunlight import config, errors

config.API_KEY=" "

def geocode(location):
    if 'test' in sys.argv:
        return None
        
    try:
        geocoder = GoogleV3()
        geocoded_location = geocoder.geocode(location)
        return geocoded_location
    except GeopyError: 
        print("Failure to geocode")
        return None
    
def find_congressional_district(lat, lon):
    if 'test' in sys.argv:
        congress_api = Congress(use_https=False)
    else:
        congress_api = Congress()
    try:
        district = congress_api.locate_districts_by_lat_lon(
            lat,
            lon
        )
        if district:
            return district[0]
    except errors.SunlightException:
        print("Failure to fetch congressional district")
        return None
        
def populate_location_and_district(instance):
    loc = geocode(instance.location)
    
    if loc:
        instance.lat = loc.latitude
        instance.lon = loc.longitude
    
        # find congressional District
        district = find_congressional_district(instance.lat, instance.lon)
    
        # use existing district if possible, otherwise create it
        if district: 
            local_district, created = District.objects.get_or_create(
                state=district['state'],
                district=district['district']
            )
            instance.district = local_district
            local_district.save()

    instance.save()