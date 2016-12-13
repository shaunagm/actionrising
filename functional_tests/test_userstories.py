import time

from .base import SeleniumTestCase
from .pageobjects import (BasicActionListPage, ActionEditPage, ProfilePage, ToDoPage,
    BasicActionDetailPage, ManageActionPage)
from profiles.models import Profile, ProfileActionRelationship

default_user = "buffysummers"
default_password = "apocalypse"

# This series of integration tests mimic fairly involved interactions on the site.

class TestAddAndFollowAction(SeleniumTestCase):
    # User creates an action, checks their page and sees it in "created" but not "tracked"
    # actions.  They check their todo list and it's not there either. So they go to the action
    # page and follow it.  They see it in "tracked" actions as well.  They go to their todo
    # list and see it there as well. Finally, they add a note.

    def test_add_and_follow_action(self):
        # Login, go to action edit page, create action
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.log_in(default_user, default_password)
        self.action_edit_form = ActionEditPage(self.browser, root_uri=self.live_server_url)
        self.action_edit_form.go_to_create_page()
        self.action_edit_form.title = "A new action to take"
        self.action_edit_form.submit_button.click()
        # Go to profile page and see action is only listed in 'created', not 'tracked'
        self.profile_page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.profile_page.go_to_profile_page(username=default_user)
        created_actions, tracked_actions = self.profile_page.get_actions()
        self.assertIn("A new action to take", created_actions)
        self.assertNotIn("A new action to take", tracked_actions)
        # Check todo list
        self.todo_page = ToDoPage(self.browser, root_uri=self.live_server_url)
        self.todo_page.go_to_todo_page(username=default_user)
        self.assertEquals(len(self.todo_page.rows), 1)
        self.assertIsNone(self.actions_table.first_row_action)
        # Go to action page and add it
        self.action_page = BasicActionDetailPage(self.browser, root_uri=self.live_server_url)
        self.action_page.go_to_detail_page(title="A new action to take")
        self.action_page.take_action_button.click()
        # Check profile page again
        self.profile_page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.profile_page.go_to_profile_page(username=default_user)
        created_actions, tracked_actions = self.profile_page.get_actions()
        self.assertIn("A new action to take", created_actions)
        self.assertIn("A new action to take", tracked_actions)
        # Now it's in the todo list too
        self.todo_page = ToDoPage(self.browser, root_uri=self.live_server_url)
        self.todo_page.go_to_todo_page(username=default_user)
        self.assertEquals(len(self.todo_page.rows), 1)
        self.assertEquals(self.actions_table.first_row_action.text, "A new action to take")
        # No notes yet
        self.todo_page.toggle_notes_button.click()
        self.assertEquals(self.todo_page.get_notes(), ["Notes: None"])
        # Let's add one!
        self.todo_page.manage_button_first_row.click()
        self.manage_action_page = ManageActionPage(self.browser, root_uri=self.live_server_url)
        self.manage_action_page.go_to_manage_action_page(url=self.browser.current_url)
        self.manage_action_page.notes = "A note! Yay!"
        self.manage_action_page.submit_button.click()
        # Let's see if it's there
        self.todo_page = ToDoPage(self.browser, root_uri=self.live_server_url)
        self.todo_page.go_to_todo_page(username=default_user)
        self.todo_page.toggle_notes_button.click()
        self.assertEquals(self.todo_page.get_notes(), ["Notes: A note! Yay!"])
