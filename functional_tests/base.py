from unittest import skipIf
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mysite.settings import SKIP_FUNCTIONAL_TESTS

@skipIf(SKIP_FUNCTIONAL_TESTS, 'Skipping functional tests')
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

    def wait_helper(cls, id="actionrisingbody"):
        element = WebDriverWait(cls.browser, 15).until(
            EC.presence_of_element_located((By.ID, id))
        )
        if not element:
            raise Exception("Page didn't load after 15 seconds")
