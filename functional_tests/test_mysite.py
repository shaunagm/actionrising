import time

from .base import SeleniumTestCase
from .pageobjects import BasePage, LoggedOutLandingPage, LoggedInLandingPage

default_user = "buffysummers"
default_password = "apocalypse"

class TestBasics(SeleniumTestCase):

    def test_login_page(self):
        base_page = BasePage(self.browser, root_uri=self.live_server_url)
        self.assertEquals(base_page.is_logged_in(), False)
        base_page.log_in(default_user, default_password)
        self.assertEquals(base_page.is_logged_in(), True)

    def test_logged_out_landing_page(self):
        landing_page = LoggedOutLandingPage(self.browser, root_uri=self.live_server_url)
        landing_page.go_to_index_if_necessary()
        landing_page.signup.click()
        self.assertEquals(landing_page.w.current_url[-15:], "invites/sign-up")

    def test_logged_in_landing_page(self):
        landing_page = LoggedInLandingPage(self.browser, root_uri=self.live_server_url)
        self.wait_helper()
        landing_page.log_in(default_user, default_password)
        self.wait_helper()
        self.assertEquals(len(landing_page.open_actions_items), 0)
        landing_page.search_actions_link.click()
        self.assertEquals(landing_page.w.current_url, self.live_server_url + "/actions/actions")
