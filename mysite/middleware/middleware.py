import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from plugins.location_plugin.models import get_timezone_given_user

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):

        # Skip for anonymous users
        if not request.user.is_authenticated:
            return

        # If user has timezone calculated, apply
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
            return

        # Try to calculate timezone
        try:
            if request.session.get('timezone_status') == "Failed":
                    timezone.deactivate()
            else:
                tz = get_timezone_given_user(request.user)
                if tz:
                    request.session['django_timezone'] = tz
                    timezone.activate(pytz.timezone(tz))
                else:
                    request.session['timezone_status'] = "Failed"
                    timezone.deactivate()
        except:
            print("Error calculating timezone")
