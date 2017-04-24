import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from plugins.location_plugin.models import get_timezone_given_user

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        elif request.session.get('timezone_status') == "Failed":
            timezone.deactivate()
        else:
            tz = get_timezone_given_user(request.user)
            if not tz:
                request.session['timezone_status'] = "Failed"
                timezone.deactivate()
            else:
                request.session['django_timezone'] = tz
