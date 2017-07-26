from .base import SeleniumTestCase

from .pageobjects import GroupListPage, GroupEditPage, GroupProfilePage

default_user = "buffysummers"
default_password = "apocalypse"

class TestGroups(SeleniumTestCase):

    def test_group_views(self):
        '''This test case is just to cover the basics.  I'll update it and break it out into
        separate tests once we get all the functionality in our views.'''
        self.groupform = GroupEditPage(self.browser, root_uri=self.live_server_url)
        # assert we get redirected to login
        self.groupform.go_to_create_page()
        self.assertEquals(self.browser.title, "ActionRising Login")
        # Login
        self.groupform.log_in(default_user, default_password)
        self.groupform.go_to_create_page()
        self.assertNotEquals(self.browser.title, "ActionRising Login")
        # Add data
        self.groupform.groupname = "A Test Group"
        self.groupform.select_privacy("Visible to public")
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.groupform.summary)
        self.groupform.summary = "A quick summary"
        self.groupform.submit_button.click()
        self.assertNotEquals(self.browser.title, "ActionRising Login") # Success url correct?
        # Check data
        self.groupdetail = GroupProfilePage(self.browser, root_uri=self.live_server_url)
        self.groupdetail.go_to_profile_page(name="A Test Group")
        self.assertEquals(self.groupdetail.group_name.text, "A Test Group")
        self.assertEquals(self.groupdetail.privacy.text, "Visible to public")
        self.assertEquals(self.groupdetail.summary.text, "A quick summary")
        self.assertEquals(len(self.groupdetail.member), 1) # Only creator should be member
        self.assertIsNotNone(self.groupdetail.admin_button)
        self.assertIsNotNone(self.groupdetail.edit_button)
        # Edit data
        self.groupform = GroupEditPage(self.browser, root_uri=self.live_server_url)
        self.groupform.go_to_update_page(name="A Test Group")
        self.assertFalse(self.groupform.groupname.is_displayed())
        self.groupform.select_privacy("Visible sitewide")
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.groupform.summary)
        self.groupform.summary.clear()
        self.groupform.summary = "We made a change"
        self.groupform.submit_button.click()
        # Check data
        self.groupdetail = GroupProfilePage(self.browser, root_uri=self.live_server_url)
        self.groupdetail.go_to_profile_page(name="A Test Group")
        self.assertEquals(self.groupdetail.summary.text, "We made a change")
        self.assertEquals(self.groupdetail.privacy.text, "Visible sitewide")
        # Log out and try as anon user, get redirected
        self.groupdetail.log_out()
        self.groupdetail.go_to_profile_page(name="A Test Group")
        self.assertEquals(self.browser.title, "ActionRising Login")
        # Log in as non-member, see page, don't see admin or edit links
        self.groupdetail.log_in("giles", default_password)
        self.groupdetail.go_to_profile_page(name="A Test Group")
        self.assertEquals(self.groupdetail.group_name.text, "A Test Group")
        self.assertEquals(self.groupdetail.summary.text, "We made a change")
        self.assertEquals(self.groupdetail.privacy.text, "Visible sitewide")
        self.assertIsNone(self.groupdetail.admin_button)
        self.assertIsNone(self.groupdetail.edit_button)

