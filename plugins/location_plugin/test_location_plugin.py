import mock
from django.test import TestCase

from actions.models import Action
from django.contrib.auth.models import User

from plugins.location_plugin.lib import locations

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
