import time

from .base import SeleniumTestCase
from .pageobjects import (BasicActionListPage, BasicActionDetailPage, SlateDetailPage,
    SlateListPage, SlateActionsListPage)
from profiles.models import Profile, ProfileActionRelationship

default_user = "buffysummers"
default_password = "apocalypse"

class TestActionList(SeleniumTestCase):

    def setUp(self):
        super(TestActionList, self).setUp()
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.log_in(default_user, default_password)
        self.actions_table.go_to_default_actions_page_if_necessary()

    def test_display_actions(self):
        self.assertTrue(self.actions_table.datatables_js_is_enabled())
        self.assertEquals(len(self.actions_table.columns), 4)
        self.assertEquals(len(self.actions_table.rows), 4)
        self.assertEquals(self.actions_table.first_row_date.text, "Fri Dec 02")
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")
        self.assertEquals(self.actions_table.first_row_tracker_count.text, "0")
        self.assertEquals(len(self.actions_table.labels), 4)

    # def test_filter_actions_by_status(self):
    #     self.actions_table.active_only.click()
    #     self.assertEquals(len(self.actions_table.rows), 3)
    #     self.assertEquals(self.actions_table.first_row_action.text, "Donate to Planned Parenthood")

    def test_filter_actions_by_friends(self):
        self.actions_table.friends_only.click()
        self.assertEquals(len(self.actions_table.rows), 2)
        self.assertEquals(self.actions_table.first_row_action.text, "Donate to Planned Parenthood")

    def test_filter_actions_by_priority(self):
        self.actions_table.select_priority("Emergency")
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Denounce Trump's proposed appointment of Steve Bannon")
        self.actions_table.select_priority("High")
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Sign petition to make Boston a sanctuary city")
        self.actions_table.select_priority("Medium")
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Donate to Planned Parenthood")
        self.actions_table.select_priority("Low")
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")
        self.actions_table.select_priority("All")
        self.assertEquals(len(self.actions_table.rows), 4)
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")

    # TODO add test for filter by location once it's actually implemented

    # TODO add test for filter by deadline (will need a factory or something to generate
    # the right deadline data, the fixtures will quickly go out of date)

class TestActionDetail(SeleniumTestCase):

    def setUp(self):
        super(TestActionDetail, self).setUp()
        self.action_page = BasicActionDetailPage(self.browser, root_uri=self.live_server_url)
        self.action_page.log_in(default_user, default_password)
        self.action_page.go_to_detail_page(title="Denounce Trump's proposed appointment of Steve Bannon")

    def test_display_action_detail(self):
        self.assertEquals(self.action_page.creator.text, "Created by thewitch")
        self.assertEquals(self.action_page.quick_link.text, "Quick link: www.fakelinktomoreinfo.com")
        self.assertEquals(self.action_page.description.text, "Here's some instructions!")
        self.assertEquals(len(self.action_page.labels), 1)
        self.assertIsNotNone(self.action_page.comments_div)
        self.assertIsNotNone(self.action_page.add_comment_button)
        self.assertEquals(self.action_page.priority.text, "Emergency priority")
        self.assertEquals(self.action_page.privacy.text, "Visible Sitewide")
        self.assertEquals(self.action_page.status.text, "Open for action")

    def test_action_tracking_display(self):
        self.assertEquals(len(self.action_page.suggested_trackers), 1)
        self.assertEqual(self.action_page.suggested_trackers[0].text, "Faith Lehane")
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")
        self.assertEquals(len(self.action_page.done_trackers), 1)
        self.assertEqual(self.action_page.done_trackers[0].text, "Rupert Giles")

    def test_take_action(self):
        self.wait_helper()
        self.action_page.manage_action_button.click()
        self.wait_helper("manage-action-list")
        # Logged in user should now appear in accepted trackers
        self.assertEquals(len(self.action_page.accepted_trackers), 2)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Buffy Summers")
        # Now test remove action
        self.action_page.select_manage_action_option("Remove from todos")
        self.wait_helper()
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")

    def test_mark_action_as_done(self):
        self.wait_helper()
        self.action_page.manage_action_button.click()
        # Logged in user should now appear in accepted trackers but not done trackers
        self.assertEquals(len(self.action_page.accepted_trackers), 2)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Buffy Summers")
        self.assertEquals(len(self.action_page.done_trackers), 1)
        self.assertEqual(self.action_page.done_trackers[0].text, "Rupert Giles")
        # Now mark action as done
        self.action_page.mark_action_as_done_button.click()
        self.wait_helper()
        # Logged in user should now appear in done trackers but not accepted trackers
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")
        self.assertEquals(len(self.action_page.done_trackers), 2)
        self.assertEqual(self.action_page.done_trackers[0].text, "Buffy Summers")

class TestSlateList(SeleniumTestCase):

    def setUp(self):
        super(TestSlateList, self).setUp()
        self.slates_table = SlateListPage(self.browser, root_uri=self.live_server_url)
        self.slates_table.log_in(default_user, default_password)
        self.slates_table.go_to_default_slates_page_if_necessary()
        self.wait_helper()

    def test_display_slates(self):
        self.assertTrue(self.slates_table.datatables_js_is_enabled())
        self.assertEquals(len(self.slates_table.columns), 5)
        self.assertEquals(len(self.slates_table.rows), 3)
        self.assertEquals(self.slates_table.first_row_date.text, "Fri Dec 02")
        self.assertEquals(self.slates_table.first_row_slate.text, "High stakes slate of actions")
        self.assertEquals(self.slates_table.first_row_creator.text, "dru")
        self.assertEquals(self.slates_table.first_row_action_count.text, "3")

    # def test_filter_slates_by_status(self):
    #     self.slates_table.active_only.click()
    #     self.assertEquals(len(self.slates_table.rows), 2)
    #     self.assertEquals(self.slates_table.first_row_slate.text, "High stakes slate of actions")

    def test_filter_slates_by_friends(self):
        self.slates_table.friends_only.click()
        self.assertEquals(len(self.slates_table.rows), 1)
        self.assertEquals(self.slates_table.first_row_slate.text, "How to prevent an apocalypse")

class TestSlateDetail(SeleniumTestCase):

    def test_slate_detail_info(self):
        self.slate_info = SlateDetailPage(self.browser, root_uri=self.live_server_url)
        self.wait_helper()
        self.slate_info.log_in(default_user, default_password)
        self.slate_info.go_to_detail_page(title="Things to do on the Hellmouth")
        self.wait_helper()
        self.slate_info.info_tab.click()
        self.wait_helper("info")
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
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Donate to Planned Parenthood")
        self.actions_table.friends_only.click()

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
        self.assertEquals(len(self.actions_table.rows), 3)
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")

    def test_owned_slate_actions_display(self):
        '''Make sure the 5th "manage" column is included when user owns slate.'''
        self.actions_table = SlateActionsListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.log_in(default_user, default_password)
        self.actions_table.go_to_detail_page(title="Things to do on the Hellmouth")
        self.assertTrue(self.actions_table.datatables_js_is_enabled())
        self.assertEquals(len(self.actions_table.columns), 5)
