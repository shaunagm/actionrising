import time

from .base import SeleniumTestCase
from .pageobjects import BasicActionListPage, BasicActionDetailPage
from profiles.models import Profile, ProfileActionRelationship

default_user = "buffysummers"
default_password = "apocalypse"

class TestPublicActionList(SeleniumTestCase):

    def setUp(self):
        super(TestPublicActionList, self).setUp()
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.go_to_default_actions_page_if_necessary()
        self.actions = self.actions_table.get_actions()

    def test_public_action_shows(self):
        self.assertTrue("Public Test Action" in self.actions)

    def test_sitewide_action_hidden(self):
        self.assertFalse("Sitewide Test Action" in self.actions)

    def test_protected_action_hidden(self):
        self.assertFalse("Buffy Can See" in self.actions)

class TestActionList(SeleniumTestCase):

    def setUp(self):
        super(TestActionList, self).setUp()
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.log_in(default_user, default_password)
        self.actions_table.return_to_default_actions_page()

    def test_display_actions(self):
        self.assertTrue(self.actions_table.datatables_js_is_enabled())
        self.assertEquals(len(self.actions_table.columns), 4)
        self.assertEquals(self.actions_table.first_row_date.text, "Sat Apr 22")
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")
        self.assertEquals(self.actions_table.first_row_tracker_count.text, "0")
        self.assertEquals(len(self.actions_table.labels), 4)
        actions = self.actions_table.get_actions()
        self.assertTrue("Public Test Action" in actions)
        self.assertTrue("Sitewide Test Action" in actions)
        self.assertTrue("Tara's Public Action" in actions)
        self.assertTrue("Faith's Public Action" in actions)
        self.assertTrue("Buffy Can See" in actions)
        self.assertFalse("Buffy Cannot See" in actions)
        self.assertTrue("Do Bad Stuff" in actions)
        # withdrawn
        self.assertFalse("An Unproductive Action" in actions)
        self.assertTrue("Anonymous Action" in actions)

    # def test_filter_actions_by_status(self):
    #     self.actions_table.active_only.click()
    #     self.assertEquals(len(self.actions_table.rows), 3)
    #     self.assertEquals(self.actions_table.first_row_action.text, "Donate to Planned Parenthood")

    def test_filter_actions_by_friends(self):
        self.actions_table.friends_only.click()
        actions = self.actions_table.get_actions()
        # no relationship between vampire and buffy
        self.assertFalse("Do Bad Stuff" in actions)
        # faith follows buffy
        self.assertFalse("Faith's Public Action" in actions)
        # buffy and thewitch follow each other
        self.assertTrue("Buffy Can See" in actions)
        # buffy follows tara
        self.assertTrue("Tara's Public Action" in actions)
        self.assertFalse("Anonymous Action" in actions)

    def test_filter_actions_by_priority(self):
        self.actions_table.select_priority("Emergency")
        self.assertEquals(len(self.actions_table.rows), 8)
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")
        self.actions_table.select_priority("High")
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Sign petition to make Boston a sanctuary city")
        self.actions_table.select_priority("Medium")
        self.assertEquals(len(self.actions_table.rows), 2)
        self.assertEquals(self.actions_table.first_row_action.text, "An Action In Sacramento")
        self.actions_table.select_priority("Low")
        self.assertEquals(len(self.actions_table.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")
        self.actions_table.select_priority("All")
        self.assertEquals(len(self.actions_table.rows), 12)
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")

    def test_filter_actions_by_location_for_user_with_state_and_district(self):
        self.assertEquals(len(self.actions_table.rows), 12)
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")
        # Sort by district
        self.actions_table.select_location("My District")
        self.assertEquals(len(self.actions_table.rows), 1)
        time.sleep(4)
        self.assertEquals(self.actions_table.first_row_action.text, "Sign petition to make Boston a sanctuary city")
        # Sort by state
        self.actions_table.select_location("My State")
        self.assertEquals(len(self.actions_table.rows), 2)
        self.assertEquals(self.actions_table.first_row_action.text, "Sign petition to make Boston a sanctuary city")
        # Sort by national/global
        self.actions_table.select_location("National or Global")
        self.assertEquals(len(self.actions_table.rows), 2)
        self.assertEquals(self.actions_table.first_row_action.text, "Join the site")
        # Back to all
        self.actions_table.select_location("Anywhere")
        self.assertEquals(len(self.actions_table.rows), 12)
        self.assertEquals(self.actions_table.first_row_action.text, "Anonymous Action")

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

    def test_anonymous_action_detail(self):
        self.action_page.go_to_detail_page(title="Anonymous Action")
        self.assertEquals(self.action_page.creator.text, "Created anonymously")

    def test_action_tracking_display(self):
        self.action_page.display_tracker_link.click()
        self.wait_helper("profile_accepted")
        time.sleep(4)
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
        self.action_page.display_tracker_link.click()
        self.wait_helper("profile_accepted")
        time.sleep(4)
        self.assertEquals(len(self.action_page.accepted_trackers), 2)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Buffy Summers")
        # Now test remove action
        self.action_page.select_manage_action_option("Remove from todos")
        self.wait_helper()
        self.action_page.display_tracker_link.click()
        self.wait_helper("profile_accepted")
        time.sleep(4)
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")

    def test_mark_action_as_done(self):
        self.wait_helper()
        self.action_page.manage_action_button.click()
        self.wait_helper()
        self.action_page.display_tracker_link.click()
        self.wait_helper("profile_accepted")
        time.sleep(4)
        self.assertEquals(len(self.action_page.accepted_trackers), 2)
        # Logged in user should now appear in accepted trackers but not done trackers
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Buffy Summers")
        self.assertEquals(len(self.action_page.done_trackers), 1)
        self.assertEqual(self.action_page.done_trackers[0].text, "Rupert Giles")
        # Now mark action as done
        self.action_page.mark_action_as_done_button.click()
        self.wait_helper()
        # Logged in user should now appear in done trackers but not accepted trackers
        self.action_page.display_tracker_link.click()
        self.wait_helper("profile_accepted")
        time.sleep(4)
        self.assertEquals(len(self.action_page.accepted_trackers), 1)
        self.assertEqual(self.action_page.accepted_trackers[0].text, "Willow")
        self.assertEquals(len(self.action_page.done_trackers), 2)
        self.assertEqual(self.action_page.done_trackers[0].text, "Buffy Summers")

class TestShareAction(SeleniumTestCase):

    def setUp(self):
        super(TestShareAction, self).setUp()
        self.action_page = BasicActionDetailPage(self.browser, root_uri=self.live_server_url)
        self.action_page.log_in(default_user, default_password)

    def test_share_public_action(self):
        self.action_page.go_to_detail_page(title="Public Test Action")
        self.assertIsNotNone(self.action_page.share)

    def test_share_sitewide_action(self):
        self.action_page.go_to_detail_page(title="Sitewide Test Action")
        self.assertEqual(self.action_page.share, None)

    def test_share_follows_action(self):
        self.action_page.go_to_detail_page(title="Buffy Can See")
        self.assertEqual(self.action_page.share, None)
