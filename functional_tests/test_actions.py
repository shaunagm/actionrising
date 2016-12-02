import time

from .base import SeleniumTestCase
from .pageobjects import BasicActionPage, BasicActionDetailPage

default_user = "buffysummers"
default_password = "apocalypse"

class TestActions(SeleniumTestCase):

    def setUp(self):
        super(TestActions, self).setUp()
        self.actions_table = BasicActionPage(self.browser, root_uri=self.live_server_url)
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

    def test_filter_actions_by_status(self):
        self.actions_table.active_only.click()
        self.assertEquals(len(self.actions_table.rows), 3)
        self.assertEquals(self.actions_table.first_row_action.text, "Donate to Planned Parenthood")

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

    def test_action_tracking(self):
        self.assertEquals(len(self.action_page.suggested_trackers), 1)
        self.assertEqual(self.action_page.suggested_trackers[0].text, "Faith Lehane")
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")
        self.assertEquals(len(self.action_page.done_trackers), 1)
        self.assertEqual(self.action_page.done_trackers[0].text, "Rupert Giles")

    def test_take_action(self):
        self.action_page.take_action_button.click()
        # Logged in user should now appear in accepted trackers
        self.assertEquals(len(self.action_page.accepted_trackers), 2)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Buffy Summers")
        # Now remove action
        self.action_page.select_manage_action_option("Remove Action")
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")

    def test_mark_action_as_done(self):
        self.action_page.take_action_button.click()
        # Logged in user should now appear in accepted trackers
        self.assertEquals(len(self.action_page.accepted_trackers), 2)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Buffy Summers")
        self.assertEquals(len(self.action_page.done_trackers), 1)
        self.assertEqual(self.action_page.done_trackers[0].text, "Rupert Giles")
        # Now mark action as done
        self.action_page.select_manage_action_option("Mark as Done")
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")
        self.assertEquals(len(self.action_page.done_trackers), 2)
        self.assertEqual(self.action_page.done_trackers[0].text, "Buffy Summers")
