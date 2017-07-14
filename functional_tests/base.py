from importlib import import_module
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
from django.contrib.auth.models import User
from unittest import skipIf
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@skipIf(settings.SKIP_FUNCTIONAL_TESTS, 'Skipping functional tests')
class SeleniumTestCase(StaticLiveServerTestCase):

    fixtures = ['fixtures.json']

    """Test case for Selenium-driven functional tests."""

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Chrome(settings.CHROMEDRIVER_PATH)
        super(SeleniumTestCase, cls).setUpClass()

    def setUp(self):
        super(SeleniumTestCase, self).setUp()
        if not self.browser.current_url.startswith(self.live_server_url):
            self.browser.get(self.live_server_url)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()

    def wait_helper(self, id="actionrisingbody"):
        """ Make sure element is visible on page """
        element = WebDriverWait(self.browser, 15).until(
            EC.visibility_of_element_located((By.ID, id))
        )
        if not element:
            raise Exception("Page didn't load after 15 seconds")

    def force_login(self, user):
        # mostly taken from django-selenium-login
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

        session = SessionStore()
        session[SESSION_KEY] = user.id
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()

        cookie = {
            'name': settings.SESSION_COOKIE_NAME,
            'value': session.session_key,
            'path': '/',
            'domain': self.server_thread.host,  # self.host after 1.11
        }

        self.browser.add_cookie(cookie)


class QuickLogin(object):
    default_user = "buffysummers"

    def setUp(self):
        super(QuickLogin, self).setUp()
        user = User.objects.get(username=self.default_user)
        self.force_login(user)
