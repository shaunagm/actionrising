import pytz, traceback
from geopy.geocoders import GoogleV3

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from plugins.location_plugin.models import Location

class TimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):

        # Skip for anonymous users
        if not request.user.is_authenticated:
            timezone.activate(pytz.timezone('America/New_York'))
            return

        # If user is coming from edit profile, where they may have edited location,
        # try to calculate timezone
        if "/profiles/edit" in request.META.get('HTTP_REFERER', ''):
            loc = self.get_location(request.user)
            if loc:
                tz = self.get_timezone(loc)
                if tz:
                    request.session['django_timezone'] = tz
            else:
                request.session['django_timezone'] = None

        # If user has timezone calculated, apply
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.activate(pytz.timezone('America/New_York'))

    def get_location(self, user):
        ctype = ContentType.objects.get_for_model(user.profile)
        location = Location.objects.filter(content_type=ctype, object_id=user.profile.pk).first()
        if location and location.lat and location.lon:
            return location

    def get_timezone(self, location):
        try:
            geocoder = GoogleV3()
            tz = geocoder.timezone([location.lat, location.lon])
            if tz:
                return tz.zone
        except:
            traceback.print_exc()
