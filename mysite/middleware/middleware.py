import pytz, traceback
from geopy.geocoders import GoogleV3

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from plugins.location_plugin.models import Location

DEFAULT_TIMEZONE = 'America/New_York'

class TimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):
        '''Middleware gets timezone for all views, updates when referred to by
        /profiles/edit, the only place where location can be updated'''
        if not request.user.is_authenticated:
            timezone.activate(pytz.timezone(DEFAULT_TIMEZONE))
            return

        if "/profiles/edit" in request.META.get('HTTP_REFERER', ''):
            request.session['django_timezone'] = self.update_timezone(request)

        self.activate_timezone(request.session.get('django_timezone'))

    def update_timezone(self, request):
        '''Update timezone if location & timezone exists, or if location has been
        removed, otherwise return current timezone'''
        loc = self.get_location(request.user)
        if loc:
            tz = self.get_timezone(loc)
            return tz if tz else request.session.get('django_timezone')
        else:
            return None

    def get_location(self, user):
        '''Get location with lat/lon specified'''
        ctype = ContentType.objects.get_for_model(user.profile)
        location = Location.objects.filter(content_type=ctype, object_id=user.profile.pk).first()
        if location and location.lat and location.lon:
            return location

    def get_timezone(self, location):
        '''Get timezone given location'''
        try:
            geocoder = GoogleV3()
            tz = geocoder.timezone([location.lat, location.lon])
            if tz:
                return tz.zone
        except:
            traceback.print_exc()

    def activate_timezone(self, tzname):
        '''If user has timezone set, apply'''
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.activate(pytz.timezone(DEFAULT_TIMEZONE))
