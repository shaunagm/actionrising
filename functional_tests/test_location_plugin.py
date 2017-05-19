import time
from .base import SeleniumTestCase
from .pageobjects import BasicActionDetailPage, ProfilePage, EditProfilePage

default_user = "giles"
default_password = "apocalypse"

class TestTimezoneChange(SeleniumTestCase):

    def navigate_to_editprofile(self):
        self.page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.page.go_to_profile_page(username=default_user)
        self.page.edit_page_button.click()
        self.page = EditProfilePage(self.browser, root_uri=self.live_server_url)

    def navigate_to_detail(self):
        self.page = BasicActionDetailPage(self.browser, root_uri=self.live_server_url)
        self.page.go_to_detail_page(title="Sign petition to make Boston a sanctuary city")

    def test_tz(self):
        self.navigate_to_detail()
        # Test for logged out user - should display in eastern
        self.assertEqual(self.page.deadline.text, "Deadline May 18, 2017, 3:58 p.m.")
        # Test for logged in user with no location set - should display in eastern
        self.page.log_in(default_user, default_password)
        self.navigate_to_detail()
        self.assertEqual(self.page.deadline.text, "Deadline May 18, 2017, 3:58 p.m.")
        # Test changes when location added - add chicago - should display in chicago
        self.navigate_to_editprofile()
        self.page.location.clear()
        self.page.location = "Chicago, IL"
        self.page.submit_button.click()
        self.navigate_to_detail()
        self.assertEqual(self.page.deadline.text, "Deadline May 18, 2017, 2:58 p.m.")
        # Test doesn't change when non-location field on profile is edited - should display in chicago
        self.navigate_to_editprofile()
        self.page.last_name.clear()
        self.page.last_name = "Giiiiiiillllles"
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.page.submit_button)
        self.page.submit_button.click()
        self.navigate_to_detail()
        self.assertEqual(self.page.deadline.text, "Deadline May 18, 2017, 2:58 p.m.")
        # Test does change when location changed - add sacramento - should display in california
        self.navigate_to_editprofile()
        self.page.location.clear()
        self.page.location = "Sacramento, CA"
        self.page.submit_button.click()
        self.navigate_to_detail()
        self.assertEqual(self.page.deadline.text, "Deadline May 18, 2017, 12:58 p.m.")
        # Test does change when location removed (back to default) - should display in eastern
        self.navigate_to_editprofile()
        self.page.location.clear()
        self.page.submit_button.click()
        self.navigate_to_detail()
        self.assertEqual(self.page.deadline.text, "Deadline May 18, 2017, 3:58 p.m.")
