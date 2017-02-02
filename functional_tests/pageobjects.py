import time, sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from page_objects import PageObject, PageElement, MultiPageElement

from django.contrib.auth.models import User
from actions.models import Action
from slates.models import Slate

def wait_helper(browser, id="actionrisingbody"):
    element = WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.ID, id))
    )
    if not element:
        raise Exception("Page didn't load after 15 seconds")

# Util/Base Pages

class LoginPage(PageObject):
    username = PageElement(id_='id_username')
    password = PageElement(id_="id_password")
    login = PageElement(css='form button')
    form = PageElement(tag_name='form')
    log_button = PageElement(class_name='log_button')

    def go_to_login(self):
        self.w.get(self.root_uri)
        wait_helper(self.w) # Wait until the page is loaded to click "login"
        if self.log_button:
            self.log_button.click()

    def log_in(self, username, password):
        self.go_to_login()
        wait_helper(self.w, "id_password") # Wait until the form is loaded to begin filling it out
        self.username = username
        self.password = password
        self.login.click()
        wait_helper(self.w) # Wait until the page is loaded to proceed

class BasePage(PageObject):
    navbar_links = MultiPageElement(css=".navbar a")
    account_dropdown = PageElement(id_="account_dropdown")
    account_dropdown_links = MultiPageElement(css="#account_dropdown_menu a")

    def go_to_index_if_necessary(self):
        if not self.navbar_links:
            self.w.get(self.root_uri)

    def log_in(self, username, password):
        '''Make it easy to log in from all pages'''
        login_page = LoginPage(self.w, root_uri=self.root_uri)
        login_page.go_to_login()
        login_page.log_in(username=username, password=password)

    def log_out(self):
        self.account_dropdown.click()
        for link in self.account_dropdown_links:
            if link.text == "Log Out":
                link.click()

class LoggedOutLandingPage(BasePage):
    signup = PageElement(link_text="Sign Up")
    public_actions = PageElement(link_text="actions")
    public_slates = PageElement(link_text="slates")

class LoggedInLandingPage(BasePage):
    search_actions_link = PageElement(partial_link_text="actions you can take")
    open_actions_list = PageElement(id_="open-actions")
    open_actions_items = MultiPageElement(css="tr")

class BaseListPage(BasePage):
    datatables_search_field = PageElement(css="input[type='search']")
    # Controls for all datatables-enabled lists
    active_only = PageElement(id_="filter-active-button")
    friends_only = PageElement(id_="filter-friends-button")
    sort_buttons = MultiPageElement(css=".sorting")
    # Data for all datatables-enabled lists
    columns = MultiPageElement(css=".main-list thead th")
    rows = MultiPageElement(css=".main-list tbody tr")

    def datatables_js_is_enabled(self):
        if self.datatables_search_field:
            return True
        return False

class BasicActionListPage(BaseListPage):
    action_table = MultiPageElement(id_="actions")
    # Additional Action Data
    first_row_date = PageElement(css=".odd > td:nth-child(1)")
    first_row_action = PageElement(css=".odd > td:nth-child(2)")
    first_row_tags = PageElement(css=".odd > td:nth-child(3)")
    first_row_tracker_count = PageElement(css=".odd > td:nth-child(4)")
    labels = MultiPageElement(css="span.label")
    action_tds = MultiPageElement(css=".main-list tbody tr > td:nth-child(2)")
    # Additional Action Controls
    filter_location_dropdown = PageElement(id_="filter-location-group")
    filter_location_links = MultiPageElement(css=".filter-location, .nested-link")
    filter_priority_dropdown = PageElement(id_="filter-priority-group")
    filter_priority_links = MultiPageElement(css=".filter-priority")
    filter_deadline_dropdown = PageElement(id_="filter-deadline-group")
    filter_deadline_links = MultiPageElement(css=".filter-deadline")

    def return_to_default_actions_page(self):
        self.w.get(self.root_uri + "/actions/actions")

    def go_to_public_actions_page(self):
        self.w.get(self.root_uri + "/actions/public-actions")

    def go_to_default_actions_page_if_necessary(self):
        if not self.action_table:
            # This is a decent guess at where we want to be
            self.w.get(self.root_uri + "/actions/actions")

    def select_priority(self, selection):
        self.filter_priority_dropdown.click()
        for link in self.filter_priority_links:
            if link.text == selection:
                link.click()

    def select_location(self, selection):
        self.filter_location_dropdown.click()
        for link in self.filter_location_links:
            if link.text == selection:
                link.click()

    def get_actions(self):
        actions = []
        for action in self.action_tds:
            actions.append(action.text)
        return actions

class SlateActionsListPage(BasicActionListPage):

    def go_to_detail_page(self, title=None):
        if title:
            self.slate = Slate.objects.get(title=title)
        else:
            self.slate = Slate.objects.last()
        self.w.get(self.root_uri + self.slate.get_absolute_url())

class SlateListPage(BaseListPage):
    slates_table = MultiPageElement(id_="slates")
    first_row_date = PageElement(css=".odd > td:nth-child(1)")
    first_row_slate = PageElement(css=".odd > td:nth-child(2)")
    first_row_creator = PageElement(css=".odd > td:nth-child(3)")
    first_row_action_count = PageElement(css=".odd > td:nth-child(4)")

    def go_to_default_slates_page(self):
        self.w.get(self.root_uri + "/slates/slates")

class BaseObjectDetailPage(BasePage):
    creator = PageElement(id_="created_by")
    quick_link = PageElement(id_="quick_link")
    description = PageElement(id_="description")
    priority = PageElement(id_="priority-info")
    location = PageElement(id_="location-info")
    privacy = PageElement(id_="privacy-info")
    status = PageElement(id_="status-info")
    deadline = PageElement(id_="deadline-info")

class BasicActionDetailPage(BaseObjectDetailPage):
    labels = MultiPageElement(css="span.label")
    comments_div = PageElement(id_="comment-sidebar")
    add_comment_button = PageElement(id_="add_comment_button")
    display_tracker_link = PageElement(id_="display_people_trackers")
    suggested_trackers = MultiPageElement(css="#profile_sug a")
    accepted_trackers = MultiPageElement(css="#profile_ace a")
    done_trackers = MultiPageElement(css="#profile_don a")
    display_slate_tracker_link = PageElement(id_="display_slate_trackers")
    suggested_slate_trackers = MultiPageElement(css="#slate_sug a")
    accepted_slate_trackers = MultiPageElement(css="#slate_ace a")
    done_slate_trackers = MultiPageElement(css="#slate_don a")
    manage_action_button = PageElement(id_="manage-action-button")
    mark_action_as_done_button = PageElement(id_="mark_as_done")
    commitment_button = PageElement(id_="commitment_btn")
    manage_action_links = MultiPageElement(css=".manage-action-links")

    def go_to_detail_page(self, title=None):
        if title:
            self.action = Action.objects.get(title=title)
        else:
            self.action = Action.objects.last()
        self.w.get(self.root_uri + self.action.get_absolute_url())

    def select_manage_action_option(self, selection):
        self.manage_action_button.click()
        for link in self.manage_action_links:
            if link.text == selection:
                link.click()
                break

class SlateDetailPage(BaseObjectDetailPage):
    actions_tab = PageElement(id_="#actionslink")
    info_tab = PageElement(id_="infolink")
    comments_tab = PageElement(id_="commentslink")
    hidden_actions = PageElement(css=".hidden-actions")

    def go_to_detail_page(self, title=None):
        if title:
            self.slate = Slate.objects.get(title=title)
        else:
            self.slate = Slate.objects.last()
        self.w.get(self.root_uri + self.slate.get_absolute_url())

class ActionEditPage(BasePage):
    title = PageElement(id_="id_title")
    anonymize = PageElement(id_="id_anonymize")
    main_link = PageElement(id_="id_main_link")
    priority = PageElement(id_="id_priority")
    location = PageElement(id_="id_location")
    status = PageElement(id_="id_status")
    deadline = PageElement(id_="id_deadline")
    topics = PageElement(id_="id_topics")
    types_of_action = PageElement(id_="id_actiontypes")
    submit_button = PageElement(css=".action-submit-button")

    def go_to_create_page(self):
        self.w.get(self.root_uri + "/actions/create")

    def go_to_edit_page(self, title=None, username=None):
        if title:
            self.action = Action.objects.get(title=title)
        else:
            user = User.objects.get(username=username)
            self.action = user.action_set.first()
        self.w.get(self.root_uri + self.action.get_edit_url())

    def select_privacy(self, selection):
        select = Select(self.w.find_element_by_id('id_privacy'))
        select.select_by_visible_text(selection)

    def select_status(self, selection):
        select = Select(self.w.find_element_by_id('id_status'))
        select.select_by_visible_text(selection)

class ProfilePage(BasePage):
    name = PageElement(id_="profile-username")
    actions_created = MultiPageElement(css="div#created-actions-div tbody tr .actiondetails")
    actions_tracked = MultiPageElement(css="div#tracked-actions-div tbody tr .actiondetails")

    def go_to_profile_page(self, username=None):
        user = User.objects.get(username=username)
        self.w.get(self.root_uri + user.profile.get_absolute_url())

    def get_created_actions(self):
        action_names = []
        for action in self.actions_created:
            action_names.append(action.text)
        return action_names

    def get_tracked_actions(self):
        action_names = []
        for action in self.actions_tracked:
            action_names.append(action.text)
        return action_names

    def get_actions(self):
        return self.get_created_actions(),self.get_tracked_actions()

class ToDoPage(BasicActionListPage):
    suggested_actions_link = PageElement(id_="suggested_actions_button")
    toggle_notes_button = PageElement(id_="show-notes")
    notes_rows = MultiPageElement(css="tr.notesrow")
    manage_button_first_row = PageElement(css="span.glyphicon-wrench")

    def go_to_todo_page(self, username=None):
        user = User.objects.get(username=username)
        self.w.get(self.root_uri + "/profiles/todo/")

    def get_notes(self):
        notes = []
        for note in self.notes_rows:
            notes.append(note.text)
        return notes

class ManageActionPage(BasePage):
    notes = PageElement(id_="id_notes")
    submit_button = PageElement(css=".manage-action-submit")

    def go_to_manage_action_page(self, url):
        self.w.get(url)

class CommitmentPage(BasePage):
    form_header = PageElement(css="div#form-explanation h2")
    buddies = PageElement(id_="id_buddies")
    offsite_buddies = PageElement(id_="id_offsite_buddies")
    tries = PageElement(id_="id_tries")
    message = PageElement(id_="id_message")
    days_before_emailing = PageElement(id_="id_days_before_emailing")
    submit_button = PageElement(css=".comm-submit-button")
    delete_link = PageElement(css=".comm-delete")

    def go_to_commitment_page(self, url):
        self.w.get(url)
