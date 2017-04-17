import time

from .base import SeleniumTestCase
from .pageobjects import PhonescriptCreatePage, PhonescriptDetailPage

default_user = "buffysummers"
default_password = "apocalypse"

class TestPhonescriptActionDetail(SeleniumTestCase):

    def setUp(self):
        super(TestPhonescriptActionDetail, self).setUp()
        # Login and create phonescript action (serves as super simple test of create page)
        self.phonescript_page = PhonescriptCreatePage(self.browser, root_uri=self.live_server_url)
        self.phonescript_page.log_in(default_user, default_password)
        self.phonescript_page.go_to_create_page()
        # Add details
        self.phonescript_page.details_tab.click()
        self.phonescript_page.title = "Woo a title"
        # Add default script
        self.phonescript_page.default_script_tab.click()
        self.phonescript_page.default_script_content = "Woo a default script"
        # Add constituent script
        self.phonescript_page.constituent_script_tab.click()
        self.phonescript_page.conscript_1_content = "A constituent script for senators"
        self.phonescript_page.select_rep_type("Senator")
        # Add universal script
        # pass for now
        # Submit
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.phonescript_page.submit_button)
        self.phonescript_page.submit_button.click()

    def test_logged_in_user(self):
        self.phonescript_page = PhonescriptDetailPage(self.browser, root_uri=self.live_server_url)
        self.assertEquals(len(self.phonescript_page.script_panels), 3)
        # Should probably add test to check that it's got one default and two constituent scripts here

    # def test_logged_out_user(self):
    #     time.sleep(90)
    #     pass
