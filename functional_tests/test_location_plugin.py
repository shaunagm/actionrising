import time
from .base import SeleniumTestCase
from .pageobjects import (BasicActionDetailPage, BasicActionListPage, ProfilePage,
    EditProfilePage)

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

class TestHiddenLocation(SeleniumTestCase):

    def test_can_sort_actions_with_hidden_location(self):
        # Hide location
        self.page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.page.log_in("buffysummers", "apocalypse")
        self.page.go_to_profile_page(username="buffysummers")
        self.page.edit_page_button.click()
        self.page = EditProfilePage(self.browser, root_uri=self.live_server_url)
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.page.hide_location)
        self.page.hide_location.click()
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.page.submit_button)
        self.page.submit_button.click()
        # The rest of this test is copied from test_actions
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.return_to_default_actions_page()
        # Sort actions
        self.assertEquals(len(self.actions_table.rows), 12)
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")
        # Sort by district
        self.actions_table.select_location("My District")
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Sign petition to make Boston a sanctuary city")
        # Sort by state
        self.actions_table.select_location("My State")
        self.assertEquals(len(self.actions_table.rows), 2)
        self.assertEquals(self.actions_table.first_row_action.text, "Sign petition to make Boston a sanctuary city")
        # Sort by national/global
        self.actions_table.select_location("National or Global")
        self.assertEquals(len(self.actions_table.rows), 9)
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")
        # Back to all
        self.actions_table.select_location("Anywhere")
        self.assertEquals(len(self.actions_table.rows), 12)
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")
