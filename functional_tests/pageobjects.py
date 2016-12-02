import time, sys
from page_objects import PageObject, PageElement, MultiPageElement

from actions.models import Action

# Util/Base Pages

class LoginPage(PageObject):
    username = PageElement(id_='id_username')
    password = PageElement(id_="id_password")
    login = PageElement(css='form button')
    form = PageElement(tag_name='form')
    log_button = PageElement(class_name='log_button')

    def go_to_login(self):
        self.w.get(self.root_uri)
        self.log_button.click()

    def log_in(self, username, password):
        self.go_to_login()
        self.username = username
        self.password = password
        self.login.click()

class BasePage(PageObject):
    navbar_links = MultiPageElement(css=".navbar a")
    log_button = PageElement(class_name='log_button')

    def go_to_index_if_necessary(self):
        if not self.navbar_links:
            self.w.get(self.root_uri)

    def is_logged_in(self):
        self.go_to_index_if_necessary()
        if len(self.navbar_links) == 11 and self.log_button.text == "Log Out":
            return True
        if len(self.navbar_links) != 11 and self.log_button.text == "Log In":
            return False
        raise RuntimeError("Login/logout status is inconsistent.  Navbar links number %s " \
            "and log button text is %s" % (str(len(self.navbar_links)), self.log_button.text))

    def log_in(self, username, password):
        '''Make it easy to log in from all pages'''
        login_page = LoginPage(self.w, root_uri=self.root_uri)
        login_page.go_to_login()
        login_page.log_in(username=username, password=password)

class LoggedOutLandingPage(BasePage):
    request_account = PageElement(link_text="Request an account.")

class LoggedInLandingPage(BasePage):
    search_actions_link = PageElement(partial_link_text="actions you can take")
    open_actions_list = PageElement(id_="open-actions")
    open_actions_items = MultiPageElement(css="tr")

class BasicActionPage(BasePage):
    action_table = MultiPageElement(id_="actions")
    datatables_search_field = PageElement(css="input[type='search']")
    # Action Data
    columns = MultiPageElement(css="#actions thead th")
    rows = MultiPageElement(css="#actions tbody tr")
    labels = MultiPageElement(css="span.label")
    first_row_date = PageElement(css=".odd > td:nth-child(1)")
    first_row_action = PageElement(css=".odd > td:nth-child(2)")
    first_row_tags = PageElement(css=".odd > td:nth-child(3)")
    first_row_tracker_count = PageElement(css=".odd > td:nth-child(4)")
    # Action Controls
    sort_buttons = MultiPageElement(css=".sorting")
    active_only = PageElement(id_="filter-active-button")
    friends_only = PageElement(id_="filter-friends-button")
    local_only = PageElement(id_="filter-local")
    filter_priority_dropdown = PageElement(id_="filter-priority-group")
    filter_priority_links = MultiPageElement(css=".filter-priority")
    filter_deadline_dropdown = PageElement(id_="filter-deadline-group")
    filter_deadline_links = MultiPageElement(css=".filter-deadline")

    def go_to_default_actions_page_if_necessary(self):
        if not self.action_table:
            # This is a decent guess at where we want to be
            self.w.get(self.root_uri + "/actions/actions")

    def datatables_js_is_enabled(self):
        self.go_to_default_actions_page_if_necessary()
        if self.datatables_search_field:
            return True
        return False

    def select_priority(self, selection):
        self.filter_priority_dropdown.click()
        for link in self.filter_priority_links:
            if link.text == selection:
                link.click()

class BasicActionDetailPage(BasePage):
    creator = PageElement(id_="created_by")
    quick_link = PageElement(id_="quick_link")
    description = PageElement(id_="description")
    labels = MultiPageElement(css="span.label")
    comments_div = PageElement(id_="comment-sidebar")
    add_comment_button = PageElement(id_="add_comment_button")
    suggested_trackers = MultiPageElement(css="#sug a")
    accepted_trackers = MultiPageElement(css="#ace a")
    done_trackers = MultiPageElement(css="#don a")
    take_action_button = PageElement(id_="manage-action-button")
    manage_action_links = MultiPageElement(css=".manage-action-links")

    def go_to_detail_page(self, title=None):
        if title:
            action = Action.objects.get(title=title)
        else:
            action = Action.objects.last()
        self.w.get(self.root_uri + action.get_absolute_url())

    def select_manage_action_option(self, selection):
        self.take_action_button.click()
        for link in self.manage_action_links:
            if link.text == selection:
                link.click()
                break
