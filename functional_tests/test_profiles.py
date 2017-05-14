import time
from .base import SeleniumTestCase
from .pageobjects import ProfileListPage, ProfilePage, FollowedActivity
from mysite.settings import LOGIN_URL

default_user = "buffysummers"
default_password = "apocalypse"

# dru is public
# giles is sitewide

class TestPublicProfileList(SeleniumTestCase):

    def setUp(self):
        super(TestPublicProfileList, self).setUp()
        self.profiles_table = ProfileListPage(self.browser, root_uri=self.live_server_url)
        self.profiles_table.go_to_default_profiles_page()
        self.profiles = self.profiles_table.get_profiles()

    def test_public_profiles_show(self):
        self.assertTrue("dru" in self.profiles)

    def test_sitewide_profiles_hidden(self):
        self.assertFalse("giles" in self.profiles)

    def test_protected_profiles_hidden(self):
        self.assertFalse("thewitch" in self.profiles)

class TestProfileList(SeleniumTestCase):

    def setUp(self):
        super(TestProfileList, self).setUp()
        self.profiles_table = ProfileListPage(self.browser, root_uri=self.live_server_url)
        self.profiles_table.log_in(default_user, default_password)
        self.profiles_table.go_to_default_profiles_page()

    def test_display_profiles(self):
        self.assertTrue(self.profiles_table.datatables_js_is_enabled())
        profiles = self.profiles_table.get_profiles()
        # show all
        # public
        self.assertTrue("dru" in profiles)
        # sitewide
        self.assertTrue("giles" in profiles)
        # follows that follows buffy
        self.assertTrue("thewitch" in profiles)
        # follows that doesn't follow buffy
        self.assertTrue("tara_m" in profiles)

class TestProfileDetail(SeleniumTestCase):

    def setUp(self):
        super(TestProfileDetail, self).setUp()
        self.profile_page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.profile_page.log_in(default_user, default_password)

    def test_public_profile(self):
        self.profile_page.go_to_profile_page(username="dru")
        self.assertTrue('Drusilla' in self.profile_page.name.text)
        self.assertTrue(len(self.profile_page.get_actions()) > 0)
        self.assertIsNotNone(self.profile_page.location)

    def test_sitewide_profile(self):
        self.profile_page.go_to_profile_page(username="giles")
        self.assertTrue('Giles' in self.profile_page.name.text)
        self.assertTrue(len(self.profile_page.get_actions()) > 0)

    def test_visible_protected_profile(self):
        self.profile_page.go_to_profile_page(username="thewitch")
        self.assertTrue('Willow' in self.profile_page.name.text)
        self.assertTrue(len(self.profile_page.get_actions()) > 0)
        self.assertIsNotNone(self.profile_page.location)

    def test_anonymous_action_by_friend(self):
        self.profile_page.go_to_profile_page(username="admin")
        # admin created this anonymously
        self.assertFalse("Join the site" in self.profile_page.actions_created)

    def test_restricted_profile(self):
        self.profile_page.go_to_profile_page(username="tara_m")
        self.assertFalse('login' in self.profile_page.w.current_url)
        self.assertFalse('Tara' in self.profile_page.name.text)
        self.assertTrue('tara_m' in self.profile_page.name.text)
        self.assertIsNone(self.profile_page.location)

class TestFollowedActivity(SeleniumTestCase):

    def setUp(self):
        super(TestFollowedActivity, self).setUp()
        self.feed = FollowedActivity(self.browser, root_uri=self.live_server_url)
        self.feed.log_in(default_user, default_password)
        self.feed.go_to_feed()
        self.activity = self.feed.get_activity()

    def test_anonymous_action_by_friend(self):
        self.assertFalse("admin created Join the site" in self.activity)
        self.assertFalse("Join the site was created" in self.activity)
        self.assertFalse("Join the site was updated" in self.activity)
        self.assertFalse("Anonymous created Join the site" in self.activity)

    def test_restricted_relationships(self):
        self.assertTrue("thewitch updated Buffy Can See" in self.activity)
        self.assertTrue("admin started following you" in self.activity)
        self.assertTrue("thewitch started following admin" in self.activity)
        self.assertFalse("tara_m updated Buffy Cannot See" in self.activity)

    def test_following(self):
        # buffy doesn't follow vampire
        self.assertFalse("vampire updated Do Bad Stuff" in self.activity)
        # buffy follows thewitch and Do Bad Stuff is sitewide
        self.assertTrue("thewitch took on Do Bad Stuff" in self.activity)

class TestPublicProfileDetail(SeleniumTestCase):

    def setUp(self):
        super(TestPublicProfileDetail, self).setUp()
        self.profile_page = ProfilePage(self.browser, root_uri=self.live_server_url)

    def test_public_profile(self):
        self.profile_page.go_to_profile_page(username="dru")
        self.assertTrue('Drusilla' in self.profile_page.name.text)
        self.assertIsNotNone(self.profile_page.location)

    def test_sitewide_profile(self):
        self.profile_page.go_to_profile_page(username="giles")
        self.assertFalse('Rupert' in self.profile_page.name.text)
        self.assertTrue('giles' in self.profile_page.name.text)
        self.assertFalse('login' in self.profile_page.w.current_url)

    def test_restricted_profile(self):
        self.profile_page.go_to_profile_page(username="thewitch")
        self.assertFalse('Willow' in self.profile_page.name.text)
        self.assertTrue('thewitch' in self.profile_page.name.text)
        self.assertFalse('login' in self.profile_page.w.current_url)
