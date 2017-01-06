import sys
from actions.models import Action
from geopy.exc import GeopyError
from geopy.geocoders import GoogleV3
from sunlight.services.congress import Congress
from sunlight import config, errors

config.API_KEY=" "

STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

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
    if 'test' in sys.argv or (len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'loaddata']):
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

    if instance.location == "":  # User is likely deleting their location
        instance.lat, instance.lon, instance.state, instance.district = None, None, None, None
        instance.save()
        return

    loc = geocode(instance.location)

    if loc:
        instance.lat = loc.latitude
        instance.lon = loc.longitude

        # find congressional District
        district = find_congressional_district(instance.lat, instance.lon)

        # if district exists
        if district:
            instance.state = district['state']
            instance.district = district['state'] + "-" + str(district['district'])
        else:
            # Try grabbing the state from the loc
            try:
                state = loc.split(", ")[-1]
                if state in STATES:
                    instance.state = state
            except:
                pass

        instance.save()
