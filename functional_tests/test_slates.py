import time

from .base import SeleniumTestCase
from .pageobjects import SlateDetailPage, SlateListPage, SlateActionsListPage
from profiles.models import Profile, ProfileActionRelationship

default_user = "buffysummers"
default_password = "apocalypse"

# high stakes slate is public
# how to prevent apocalyse is sitewide

class TestPublicSlateList(SeleniumTestCase):

    def setUp(self):
        super(TestPublicSlateList, self).setUp()
        self.slates_table = SlateListPage(self.browser, root_uri=self.live_server_url)
        self.slates_table.go_to_default_slates_page()
        self.slates = self.slates_table.get_slates()

    def test_public_slate_shows(self):
        self.assertTrue("High stakes slate of actions" in self.slates)

    def test_sitewide_slate_hidden(self):
        self.assertFalse("How to prevent an apocalypse" in self.slates)

    def test_protected_slate_hidden(self):
        self.assertFalse("Slate Buffy Can See" in self.slates)

class TestSlateList(SeleniumTestCase):

    def setUp(self):
        super(TestSlateList, self).setUp()
        self.slates_table = SlateListPage(self.browser, root_uri=self.live_server_url)
        self.slates_table.log_in(default_user, default_password)
        self.slates_table.go_to_default_slates_page()
        self.wait_helper()

    def test_display_slates(self):
        self.assertTrue(self.slates_table.datatables_js_is_enabled())
        self.assertEquals(len(self.slates_table.columns), 5)
        self.assertEquals(self.slates_table.first_row_date.text, "Fri Dec 02")
        self.assertEquals(self.slates_table.first_row_slate.text, "Slate Buffy Can See")
        self.assertEquals(self.slates_table.first_row_creator.text, "thewitch")
        self.assertEquals(self.slates_table.first_row_action_count.text, "0")
        slates = self.slates_table.get_slates()
        self.assertTrue("High stakes slate of actions" in slates)
        self.assertTrue("How to prevent an apocalypse" in slates)
        self.assertTrue("Slate Buffy Can See" in slates)
        self.assertFalse("Slate Buffy Cannot See" in slates)

    # def test_filter_slates_by_status(self):
    #     self.slates_table.active_only.click()
    #     self.assertEquals(len(self.slates_table.rows), 2)
    #     self.assertEquals(self.slates_table.first_row_slate.text, "High stakes slate of actions")

    def test_filter_slates_by_friends(self):
        self.slates_table.friends_only.click()
        slates = self.slates_table.get_slates()
        self.assertEquals(len(self.slates_table.rows), 2)
        self.assertTrue("Slate Buffy Can See" in slates)
        self.assertTrue("How to prevent an apocalypse" in slates)
        self.assertFalse("High stakes slate of actions" in slates)
        self.assertFalse("Slate Buffy Cannot See" in slates)

class TestSlateDetail(SeleniumTestCase):

    def test_slate_detail_info(self):
        self.slate_info = SlateDetailPage(self.browser, root_uri=self.live_server_url)
        self.wait_helper()
        self.slate_info.log_in(default_user, default_password)
        self.slate_info.go_to_detail_page(title="Things to do on the Hellmouth")
        self.wait_helper()
        self.slate_info.info_tab.click()
        self.wait_helper("info")
        time.sleep(4)
        # TODO: No idea why creator.text is returning none here
        self.assertEquals(self.slate_info.creator.text, "Created by buffysummers")
        self.assertEquals(self.slate_info.description.text, "Indescribable.")
        self.assertEquals(self.slate_info.privacy.text, "Visible Sitewide")
        self.assertEquals(self.slate_info.status.text, "Open for action")

class TestSlateActionList(SeleniumTestCase):

    def setUp(self):
        super(TestSlateActionList, self).setUp()
        self.actions_table = SlateActionsListPage(self.browser, root_uri=self.live_server_url)
        self.wait_helper()
        self.actions_table.log_in(default_user, default_password)
        self.wait_helper()
        self.actions_table.go_to_detail_page(title="High stakes slate of actions")
        self.wait_helper()

    def test_slate_actions_display(self):
        # TODO: This breaks when run as a whole but not when run individually
        self.assertTrue(self.actions_table.datatables_js_is_enabled())
        self.assertEquals(len(self.actions_table.columns), 4)
        self.assertEquals(len(self.actions_table.rows), 3)
        self.assertEquals(self.actions_table.first_row_date.text, "Fri Dec 02")
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")
        self.assertEquals(self.actions_table.first_row_tracker_count.text, "0")
        self.assertEquals(len(self.actions_table.labels), 3)
        # TODO: Add test of toggle notes

    def test_slate_actions_button_filter(self):
        self.actions_table.friends_only.click()
        actions = self.actions_table.get_actions()
        self.assertFalse("Join the site" in actions)
        self.assertFalse("Donate to Planned Parenthood" in actions)

    def test_slate_actions_dropdown_filter(self):
        # TODO: This breaks when run as a whole but not when run individually
        # Check filter by priority
        self.actions_table.select_priority("Medium")
        self.wait_helper()
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Donate to Planned Parenthood")
        self.actions_table.select_priority("High")
        self.wait_helper()
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Sign petition to make Boston a sanctuary city")
        self.actions_table.select_priority("Low")
        self.wait_helper()
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")
        self.actions_table.select_priority("All")
        self.wait_helper()
        time.sleep(4)
        self.assertEquals(len(self.actions_table.rows), 3)
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")

    def test_owned_slate_actions_display(self):
        '''Make sure the 5th "manage" column is included when user owns slate.'''
        self.actions_table = SlateActionsListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.go_to_detail_page(title="Things to do on the Hellmouth")
        self.assertTrue(self.actions_table.datatables_js_is_enabled())
        self.assertEquals(len(self.actions_table.columns), 5)
