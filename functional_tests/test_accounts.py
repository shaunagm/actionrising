import time
from django.contrib.auth.models import User
from selenium.common.exceptions import NoAlertPresentException

from .base import SeleniumTestCase
from .pageobjects import LoginPage, AccountSettingsPage, SignupPage

facebook_test_user = "Facebook TestUser"
facebook_test_user_pwd = "apocalypsenow"
facebook_test_user_email ="facebook_kobjffl_testuser@tfbnw.net"

default_user = "buffysummers"
default_password = "apocalypse"


class TestSignupForm(SeleniumTestCase):

    def setUp(self):
        super(TestSignupForm, self).setUp()
        self.signuppage = SignupPage(self.browser, root_uri=self.live_server_url)
        self.signuppage.go_to_signup()

    def test_password(self):
        self.signuppage.email = "angel@sunnydale.edu"
        self.signuppage.username = "angel"
        self.signuppage.password = "randompassword111"
        self.signuppage.signup_button.click()

        angel = User.objects.get(username="angel")
        self.assertTrue(angel.check_password("randompassword111"))

    def test_reject_duplicate_email(self):
        self.signuppage.email = "buffy@sunnydale.edu"
        self.signuppage.username = "another_test_user"
        self.signuppage.password = "randompassword111"
        self.signuppage.signup_button.click()
        help_block = self.browser.find_elements_by_css_selector(".help-block")[0]
        self.assertEquals(help_block.text, "Email already exists")

    def test_reject_invalid_username(self):
        self.signuppage.email = "neverbeforeseenemail@noveltyemails.com"
        self.signuppage.password = "randompassword111"
        self.signuppage.username = "test user"
        self.signuppage.signup_button.click()
        help_block = self.browser.find_elements_by_css_selector(".help-block")[0]
        self.assertEquals(help_block.text, 'Enter a valid username. This value may ' \
            'contain only letters, numbers, hyphens and dashes.')

class TestAccountSettingsPage(SeleniumTestCase):

    def setUp(self):
        super(TestAccountSettingsPage, self).setUp()
        self.loginpage = LoginPage(self.browser, root_uri=self.live_server_url)
        self.loginpage.go_to_login()
        self.loginpage.login_with_fb_button.click()
        # Log in via FB
        username = self.browser.find_element_by_id("email")
        password = self.browser.find_element_by_id("pass")
        username.send_keys(facebook_test_user_email)
        password.send_keys(facebook_test_user_pwd)
        self.browser.find_element_by_id("loginbutton").click()
        time.sleep(3)
        # The following two steps may or may not be necessay
        try:
            self.browser.switch_to.alert.accept()
        except NoAlertPresentException as e:
            pass
        time.sleep(3)
        try:
            self.browser.find_element_by_name("__CONFIRM__").click()
        except:
            pass

    # TODO: set up separate test user, since FB only allows you one domain to request from
    # def test_no_disconnect_without_set_password(self):
    #     '''Tests that you can't disconnect from single oauth account without setting
    #     password'''
    #     # Test we got redirected to the right place
    #     self.assertEquals(self.browser.current_url, self.live_server_url + "/profiles/dashboard#_=_")
    #     # Now go test account settings
    #     self.accountpage = AccountSettingsPage(self.browser, root_uri=self.live_server_url)
    #     self.accountpage.go_to_settings_page()
    #     # Check that password isn't set
    #     self.assertIsNotNone(self.accountpage.set_password_button)
    #     self.assertEquals(self.accountpage.change_password_button, None)
    #     # Check that you can't disconnect from FB yet
    #     self.assertEquals(self.accountpage.disconnect_from_facebook, None)
