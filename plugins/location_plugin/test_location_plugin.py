import mock

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from actions.models import Action
from plugins.location_plugin.lib import locations
from plugins.location_plugin.models import Location
from plugins.location_plugin.templatetags import location_tags
from mysite.middleware.middleware import TimezoneMiddleware

class TestLocation(TestCase):

    def setUp(self):
        self.testing_user = User.objects.create(username="testing_user")
        self.action = Action.objects.create(title="Test Action with Location", creator=self.testing_user)

    @mock.patch('plugins.location_plugin.lib.locations.geocode')
    @mock.patch('plugins.location_plugin.lib.locations.find_congressional_district')
    def test_populate_location_and_district(self, find_congressional_district, geocode):

        geocoded_location = mock.MagicMock()
        geocoded_location.latitude = 0.0
        geocoded_location.longitude = 0.0
        geocode.return_value = geocoded_location

        find_congressional_district - mock.MagicMock()
        find_congressional_district.return_value = {"state":"MA","district":5}

        # TODO: replace this with tests of Location instance
        # locations.populate_location_and_district(self.action)
        #
        # self.assertEqual(self.action.lat, 0.0)
        # self.assertEqual(self.action.lon, 0.0)
        # self.assertEqual(self.action.state, "MA")
        # self.assertEqual(self.action.district, "MA-5")

class TestTemplateTags(TestCase):

    def setUp(self):
        # Create user with no location set
        self.user_with_unset_location = User.objects.create(username="Wesley")
        # Create user with location set and shown
        ctype = ContentType.objects.get_for_model(self.user_with_unset_location.profile)
        self.user_showing_location = User.objects.create(username="Cordelia")
        self.shown_location = Location.objects.get(content_type=ctype,
            object_id=self.user_showing_location.profile.pk)
        self.shown_location.location = "Cambridge, MA"
        self.shown_location.save()
        # Create user with location set but hidden
        self.user_hiding_location = User.objects.create(username="Kendra")
        self.hidden_location = Location.objects.get(content_type=ctype,
            object_id=self.user_hiding_location.profile.pk)
        self.hidden_location.location = "Cambridge, MA"
        self.hidden_location.hide_location = True
        self.hidden_location.save()
        # Create actionw ith location
        self.action = Action.objects.create(title="Test Action with Location",
            creator=self.user_with_unset_location)
        ctype = ContentType.objects.get_for_model(self.action)
        self.action_location = Location.objects.create(content_type=ctype,
            object_id=self.action.pk)
        self.action_location.location = "Cambridge, MA"
        self.action_location.save()

    def test_get_location(self):
        # We provide [] as the first param, it represents the empty context value
        self.assertIsNone(location_tags.get_location([], self.user_with_unset_location))
        self.assertEqual(location_tags.get_location([], self.user_showing_location),
            "Cambridge, MA")
        self.assertEqual(location_tags.get_location([], self.user_hiding_location,
            show_hidden_location=True), "Cambridge, MA")
        self.assertIsNone(location_tags.get_location([], self.user_hiding_location,
            show_hidden_location=False))
        self.assertEqual(location_tags.get_location([], self.action), "Cambridge, MA")

    def test_get_state_and_district(self):
        # We provide [] as the first param, it represents the empty context value
        self.assertEqual(location_tags.get_state_and_district([], self.user_with_unset_location),
            {'state': None, 'district': None})
        self.assertEqual(location_tags.get_state_and_district([], self.user_showing_location),
            {'state': u'MA', 'district': u'MA-5'})
        self.assertEqual(location_tags.get_state_and_district([], self.user_hiding_location,
            show_hidden_location=True), {'state': u'MA', 'district': u'MA-5'})
        self.assertEqual(location_tags.get_state_and_district([], self.user_hiding_location,
            show_hidden_location=False), {'state': None, 'district': None})
        self.assertEqual(location_tags.get_state_and_district([], self.action),
            {'state': u'MA', 'district': u'MA-5'})

class TestTimezoneMiddleware(TestCase):

    def setUp(self):
        super(TestTimezoneMiddleware, self).setUp()
        self.tm = TimezoneMiddleware()
        self.request = mock.Mock()
        self.request.META = {}
        self.request.session = {}
        self.request.user = User.objects.create(username="tz_test_user")

    def test_get_location(self):
        # Set location for user
        ctype = ContentType.objects.get_for_model(self.request.user.profile)
        location = Location.objects.get(content_type=ctype, object_id=self.request.user.profile.pk)
        location.location = "Chicago, IL"
        location.save()
        # Get location
        loc = self.tm.get_location(self.request.user)
        self.assertIsInstance(loc, Location)
        self.assertEqual(str(loc.lat)[:4], "41.8")

    def test_get_timezone(self):
        # Set location for user
        ctype = ContentType.objects.get_for_model(self.request.user.profile)
        location = Location.objects.get(content_type=ctype, object_id=self.request.user.profile.pk)
        location.location = "Chicago, IL"
        location.save()
        # Get timezone
        loc = self.tm.get_location(self.request.user)
        tz = self.tm.get_timezone(loc)
        self.assertEqual(tz, "America/Chicago")

    def test_middleware_uses_default_tz_for_anonymous_user(self):
        self.request.user = AnonymousUser()
        self.assertIsNone(self.tm.process_request(self.request))
        self.assertEqual(timezone.get_current_timezone().zone, 'America/New_York')

    def test_middleware_uses_default_tz_when_no_referer(self):
        # Set location for test user
        ctype = ContentType.objects.get_for_model(self.request.user.profile)
        location = Location.objects.get(content_type=ctype, object_id=self.request.user.profile.pk)
        location.location = "Chicago, IL"
        location.save()
        # Test with middleware
        self.assertIsNone(self.tm.process_request(self.request))
        self.assertEqual(timezone.get_current_timezone().zone, 'America/New_York')

    def test_middleware_uses_default_tz_when_non_editprofile_referer(self):
        # Set location for test user
        ctype = ContentType.objects.get_for_model(self.request.user.profile)
        location = Location.objects.get(content_type=ctype, object_id=self.request.user.profile.pk)
        location.location = "Chicago, IL"
        location.save()
        # Test with middleware
        self.request.META['HTTP_REFERER'] = "http://www.actionrising.com/actions/edit"
        self.assertIsNone(self.tm.process_request(self.request))
        self.assertEqual(timezone.get_current_timezone().zone, 'America/New_York')

    def test_middleware_uses_default_tz_when_no_location_set(self):
        # Test with middleware
        self.request.META['HTTP_REFERER'] = "http://www.actionrising.com/profiles/edit"
        self.assertIsNone(self.tm.process_request(self.request))
        self.assertEqual(timezone.get_current_timezone().zone, 'America/New_York')

    def test_middleware_sets_timezone_for_referrer_with_location(self):
        # Set location for test user
        ctype = ContentType.objects.get_for_model(self.request.user.profile)
        location = Location.objects.get(content_type=ctype, object_id=self.request.user.profile.pk)
        location.location = "Chicago, IL"
        location.save()
        # Test with middleware
        self.request.META['HTTP_REFERER'] = "http://www.actionrising.com/profiles/edit"
        self.assertIsNone(self.tm.process_request(self.request))
        self.assertEqual(timezone.get_current_timezone().zone, "America/Chicago")

    def test_middleware_removes_timezone_for_referrer_when_location_removed(self):
        # Set location for test user
        ctype = ContentType.objects.get_for_model(self.request.user.profile)
        location = Location.objects.get(content_type=ctype, object_id=self.request.user.profile.pk)
        location.location = "Chicago, IL"
        location.save()
        # Test with middleware
        self.request.META['HTTP_REFERER'] = "http://www.actionrising.com/profiles/edit"
        self.assertIsNone(self.tm.process_request(self.request))
        self.assertEqual(timezone.get_current_timezone().zone, "America/Chicago")
        # Remove location
        ctype = ContentType.objects.get_for_model(self.request.user.profile)
        location.location = ""
        location.save()
        # Test with middleware
        self.request.META['HTTP_REFERER'] = "http://www.actionrising.com/profiles/edit"
        self.assertIsNone(self.tm.process_request(self.request))
        self.assertEqual(timezone.get_current_timezone().zone, "America/New_York")
