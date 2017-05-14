import time

from .base import SeleniumTestCase
from .pageobjects import (BasicActionListPage, ActionEditPage, ProfilePage, ToDoPage,
    BasicActionDetailPage, ManageActionPage, CommitmentPage, LoggedOutLandingPage,
    SlateDetailPage)
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
        self.wait_helper()
        self.action_edit_form = ActionEditPage(self.browser, root_uri=self.live_server_url)
        self.action_edit_form.go_to_create_page()
        self.wait_helper()
        self.action_edit_form.title = "A new action to take"
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.action_edit_form.submit_button)
        self.action_edit_form.submit_button.click()
        # Go to profile page and see action is only listed in 'created', not 'tracked'
        self.profile_page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.profile_page.go_to_profile_page(username=default_user)
        self.assertIn("A new action to take", self.profile_page.get_created_content())
        self.assertNotIn("A new action to take", self.profile_page.get_tracked_actions())

        # Check todo list
        self.todo_page = ToDoPage(self.browser, root_uri=self.live_server_url)
        self.todo_page.go_to_todo_page(username=default_user)
        self.assertEquals(len(self.todo_page.rows), 1)
        self.assertIsNone(self.actions_table.first_row_action)
        # Go to action page and add it
        self.action_page = BasicActionDetailPage(self.browser, root_uri=self.live_server_url)
        self.action_page.go_to_detail_page(title="A new action to take")
        self.action_page.manage_action_button.click()
        # Check profile page again
        self.profile_page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.profile_page.go_to_profile_page(username=default_user)
        self.assertIn("A new action to take", self.profile_page.get_created_content())
        self.assertIn("A new action to take", self.profile_page.get_tracked_actions())

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

class PlayingWithPrivacySettings(SeleniumTestCase):
    # User creates an action, sets privacy to sitewide, adds to their actions.
    # Checks actions list and sees it there, checks created/tracked actions and
    # sees it there.  Changes privacy to friends only.  Checks actions list and its
    # gone.  New user (followed by first user) logs in.  They see the action
    # on first user's profile.  Second new user (not followed by first user) does
    # not see the action.
    def test_privacy_settings(self):
        # Login, go to action edit page, create action
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.wait_helper()
        self.actions_table.log_in(default_user, default_password)
        self.wait_helper()
        self.action_edit_form = ActionEditPage(self.browser, root_uri=self.live_server_url)
        self.action_edit_form.go_to_create_page()
        self.action_edit_form.title = "A new action to take"
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.action_edit_form.submit_button)
        self.action_edit_form.submit_button.click()

        # Go to action list
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.go_to_default_actions_page_if_necessary()
        self.assertIn("A new action to take", self.actions_table.get_actions())

        # Log in as unfollowed user, see action
        self.actions_table.log_out()
        self.actions_table.log_in("dru", "apocalypse")
        self.actions_table.go_to_default_actions_page_if_necessary()
        self.assertIn("A new action to take", self.actions_table.get_actions())

        # Log in as creator, edit action to change privacy setting
        self.actions_table.log_out()
        self.actions_table.log_in(default_user, default_password)
        self.action_edit_form = ActionEditPage(self.browser, root_uri=self.live_server_url)
        self.action_edit_form.go_to_edit_page(title="A new action to take")
        self.action_edit_form.select_privacy("Visible to Follows")
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.action_edit_form.submit_button)
        self.action_edit_form.submit_button.click()

        # Back to action list
        self.actions_table.go_to_default_actions_page_if_necessary()
        self.assertIn("A new action to take", self.actions_table.get_actions())

        # Log in as followed user and check default user's profile, see action
        self.actions_table.log_out()
        self.actions_table.log_in("giles", "apocalypse")
        self.actions_table.go_to_default_actions_page_if_necessary()
        self.assertIn("A new action to take", self.actions_table.get_actions())
        self.profile_page = ProfilePage(self.browser, root_uri=self.live_server_url)
        self.profile_page.go_to_profile_page(username=default_user)
        self.assertIn("buffysummers created A new action to take", self.profile_page.get_activity())

        # Log in as non-followed user and check default user's profile, no action
        self.actions_table.log_out()
        self.actions_table.log_in("dru", "apocalypse")
        self.actions_table.go_to_default_actions_page_if_necessary()
        self.assertNotIn("A new action to take", self.actions_table.get_actions())
        self.profile_page.go_to_profile_page(username=default_user)

        self.assertNotIn("buffysummers created A new action to take", self.profile_page.get_activity())

class MakeAndEditCommitment(SeleniumTestCase):
    # User tries to find an action to commit to.  Can't commit to a closed action.
    # Can't commit to an action they haven't added.  Add an action, make a commitment.
    # Go back to action page, see they can now edit it.  Edit it.  Edit it again and
    # delete it.
    def test_commitment(self):
        # Log in and go to action detail page.  Use "petition-boston-sanctuary-city" because
        # that's our user's action, so she can manipulate its status.
        self.action_page = BasicActionDetailPage(self.browser, root_uri=self.live_server_url)
        self.action_page.log_in(default_user, default_password)
        self.action_page.go_to_detail_page(title="Sign petition to make Boston a sanctuary city")
        self.assertEquals(self.action_page.commitment_button, None)
        # Add action so you can see make commitment option
        self.action_page.manage_action_button.click()
        self.wait_helper("commitment_btn")
        self.assertEquals(self.action_page.commitment_button.text, "Commit to action")
        # Close action
        self.action_edit_form = ActionEditPage(self.browser, root_uri=self.live_server_url)
        self.action_edit_form.go_to_edit_page(title="Sign petition to make Boston a sanctuary city")
        self.action_edit_form.select_status("Finished")
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.action_edit_form.submit_button)
        self.action_edit_form.submit_button.click()
        # Go back, link is gone
        self.action_page.go_to_detail_page(title="Sign petition to make Boston a sanctuary city")
        self.assertEquals(self.action_page.commitment_button, None)
        # Reopen action, link is there
        self.action_edit_form = ActionEditPage(self.browser, root_uri=self.live_server_url)
        self.action_edit_form.go_to_edit_page(title="Sign petition to make Boston a sanctuary city")
        self.action_edit_form.select_status("Open for action")
        self.browser.execute_script("return arguments[0].scrollIntoView();", self.action_edit_form.submit_button)
        self.action_edit_form.submit_button.click()
        # Go back, link is there, click it
        self.action_page.go_to_detail_page(title="Sign petition to make Boston a sanctuary city")
        self.wait_helper("commitment_btn")
        self.assertEquals(self.action_page.commitment_button.text, "Commit to action")
        self.action_page.commitment_button.click()
        # TODO: Finish this (need to look up returning/chainings page objects -- this is getting silly)
        # Add a message to the commitment form
        # Save and go back to action page, link now says to edit
        # Go to edit page, click delete link
        # Back to action page, link now says to make a commitment

class LoggedOutUser(SeleniumTestCase):
    # User creates an action, checks their page and sees it in "created" but not "tracked"
    # actions.  They check their todo list and it's not there either. So they go to the action
    # page and follow it.  They see it in "tracked" actions as well.  They go to their todo
    # list and see it there as well. Finally, they add a note.

    def test_logged_out_user(self):
        # Login, go to action edit page, create action
        self.landing_page = LoggedOutLandingPage(self.browser, root_uri=self.live_server_url)
        self.landing_page.go_to_index_if_necessary()
        self.assertEquals(self.landing_page.signup.text, "Sign Up")
        self.landing_page.public_actions.click()
        self.actions_table = BasicActionListPage(self.browser, root_uri=self.live_server_url)
        self.actions_table.return_to_default_actions_page()
        self.wait_helper()
        self.actions_table.first_row_action.click()
        self.action_page = BasicActionDetailPage(self.browser, root_uri=self.live_server_url)
        self.action_page.go_to_detail_page(title="Sign petition to make Boston a sanctuary city")
        self.action_page.display_slate_tracker_link.click()
        self.wait_helper("slate_accepted")
        time.sleep(3)
        self.assertEquals(self.action_page.accepted_slate_trackers[0].text, "High stakes slate of actions")
        self.assertEquals(len(self.action_page.accepted_slate_trackers), 1)
        self.slate_info = SlateDetailPage(self.browser, root_uri=self.live_server_url)
        self.slate_info.go_to_detail_page(title="High stakes slate of actions")
        self.wait_helper()
        self.assertEquals(self.slate_info.hidden_actions.text, "This slate has 2 private actions. Try logging in to access them.")
