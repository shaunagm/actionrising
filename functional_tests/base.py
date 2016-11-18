from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class SeleniumTestCase(StaticLiveServerTestCase):

    """Test case for Selenium-driven functional tests."""

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)  # wait 5 seconds
        super().setUp()

    def tearDown(self):
        self.browser.quit()
        super().tearDown()
