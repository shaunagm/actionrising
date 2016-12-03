from geopy.geocoders import GoogleV3
from sunlight.services.congress import Congress
from sunlight import config

config.API_KEY=" "

def geocode(location):
    geocoder = GoogleV3()
    geocoded_location = geocoder.geocode(location)
    return geocoded_location
    
def find_congressional_district(lat, lon):
    congress_api = Congress()
    district = congress_api.locate_districts_by_lat_lon(
        lat,
        lon
    )
    if district:
        return district[0]