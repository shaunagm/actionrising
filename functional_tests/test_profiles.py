from .base import SeleniumTestCase
from .pageobjects import ProfileListPage, ProfileDetailPage

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
        self.profiles_table.return_to_default_actions_page()

    def test_display_actions(self):
        self.assertTrue(self.actions_table.datatables_js_is_enabled())
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
        self.profile_page = ProfileDetailPage(self.browser, root_uri=self.live_server_url)
        self.profile_page.log_in(default_user, default_password)

    def test_public_profile(self):
        self.profile_page.go_to_detail_page(username="dru")
        # shows in full

    def test_sitewide_profile(self):
        self.profile_page.go_to_detail_page(username="giles")
        # shows in full

    def test_visible_protected_profile(self):
        self.profile_page.go_to_detail_page(username="thewitch")
        # shows in full

    def test_restricted_profile(self):
        self.profile_page.go_to_detail_page(username="tara_m")
        # shows minimal


class TestPublicProfileDetail(SeleniumTestCase):
    def setUp(self):
        super(TestProfileDetail, self).setUp()
        self.profile_page = ProfileDetailPage(self.browser, root_uri=self.live_server_url)

    def test_public_profile(self):
        self.profile_page.go_to_detail_page(username="dru")
        # shows

    def test_sitewide_profile(self):
        self.profile_page.go_to_detail_page(username="giles")
        # redirects

    def test_restricted_profile(self):
        self.profile_page.go_to_detail_page(username="thewitch")
        # redirects
