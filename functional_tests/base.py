from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver

@override_settings(DEBUG=True)
class SeleniumTestCase(StaticLiveServerTestCase):

    fixtures = ['fixtures.json']

    """Test case for Selenium-driven functional tests."""

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        super(SeleniumTestCase, cls).setUpClass()

    def setUp(self):
        self.browser.get(self.live_server_url)
        super(SeleniumTestCase, self).setUp()

    # def tearDown(self):
    #     super(SeleniumTestCase, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()
