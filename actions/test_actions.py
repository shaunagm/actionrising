import datetime

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.forms.widgets import HiddenInput

from mysite.lib.choices import PrivacyChoices, StatusChoices
from actions.forms import ActionForm
from mysite.constants import constants_table
from tags.models import Tag
from profiles import factories as profile_factories
from actions import factories as action_factories


DEFAULT_ACTION_DURATION = constants_table['DEFAULT_ACTION_DURATION']
DAYS_WARNING_BEFORE_CLOSURE = constants_table['DAYS_WARNING_BEFORE_CLOSURE']


###################
### Test models ###
###################

class TestActionMethods(TestCase):

    def setUp(self):
        self.par = profile_factories.ProfileActionRelationship(
            action__title="Test Action")
        self.action = self.par.action
        self.buffy = self.action.creator
        old_date = datetime.datetime.now(
            timezone.utc) - datetime.timedelta(days=80)
        self.old_action = action_factories.Action(date_created=old_date)
        closing_soon_date = datetime.datetime.now(
            timezone.utc) - datetime.timedelta(days=40)
        self.closing_soon_action = action_factories.Action(
            date_created=closing_soon_date)

    def test_get_tags(self):
        tag_one = Tag.objects.create(name="Test Tag One", kind="topic")
        tag_two = Tag.objects.create(name="Test Tag Two", kind="type")
        self.action.tags.add(tag_one)
        self.action.tags.add(tag_two)
        self.assertEqual(list(self.action.get_tags()), [tag_one, tag_two])

    def test_get_creator(self):
        self.assertEqual(self.action.get_visible_creator(), self.buffy)
        self.assertEqual(self.action.get_creator(), self.buffy)
        self.action.anonymize = True
        self.action.save()
        self.assertEqual(self.action.get_visible_creator(), "Anonymous")
        self.assertEqual(self.action.get_creator(), self.buffy)

    def test_get_robust_url(self):
        self.assertEqual(self.action.get_robust_url(),
            '/actions/action/test-action/')

    def test_is_active(self):
        self.action.status = StatusChoices.ready
        self.action.save()
        self.assertTrue(self.action.is_active())
        self.action.status = StatusChoices.withdrawn
        self.action.save()
        self.assertFalse(self.action.is_active())

    def test_set_close_date_when_action_created_with_never_expires(self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        action = action_factories.Action(date_created=date, never_expires=True)
        self.assertIsNone(action.close_date)

    def test_set_close_date_when_action_created_with_deadline(self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        deadline = datetime.datetime.now(
            timezone.utc) + datetime.timedelta(days=5)
        action = action_factories.Action(date_created=date, deadline=deadline)
        self.assertEqual(action.close_date, deadline)

    def test_set_close_date_when_action_created_with_never_expires_and_deadline(
        self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        deadline = datetime.datetime.now(
            timezone.utc) + datetime.timedelta(days=5)
        action = action_factories.Action(
            date_created=date, deadline=deadline, never_expires=True)
        self.assertIsNone(action.close_date)

    def test_set_close_date_when_action_created_with_neither_never_expires_or_deadline(self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        action = action_factories.Action(date_created=date)
        self.assertEqual(action.close_date, date + datetime.timedelta(
            days=DEFAULT_ACTION_DURATION))

    def test_set_close_date_on_action_update_never_expires_added(self):
        self.closing_soon_action.never_expires = True
        self.closing_soon_action.save()
        self.assertIsNone(self.closing_soon_action.close_date)

    def test_set_close_date_on_action_update_never_expires_removed(self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        action = action_factories.Action(date_created=date, never_expires=True)
        action.never_expires = False
        action.save()
        self.assertEqual(action.close_date, date + datetime.timedelta(
            days=DEFAULT_ACTION_DURATION))

    def test_set_close_date_on_action_update_deadline_removed(self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        deadline = datetime.datetime.now(
            timezone.utc) + datetime.timedelta(days=5)
        action = action_factories.Action(date_created=date, deadline=deadline)
        action.deadline = None
        action.save()
        self.assertEqual(action.close_date,
            date + datetime.timedelta(days=DEFAULT_ACTION_DURATION))

    def test_set_close_date_on_action_update_deadline_added(self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        action = action_factories.Action(date_created=date)
        deadline = datetime.datetime.now(
            timezone.utc) + datetime.timedelta(days=5)
        action.deadline = deadline
        action.save()
        self.assertEqual(action.close_date, deadline)

    def test_set_close_date_on_action_update_no_deadline_info_changed(self):
        date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30)
        action = action_factories.Action(date_created=date)
        action.description = "Let's change things up!"
        action.save()
        self.assertEqual(action.close_date,
            date + datetime.timedelta(days=DEFAULT_ACTION_DURATION))

    def test_days_until(self):
        future_date = datetime.datetime.now(timezone.utc) + datetime.timedelta(
            days=21)
        self.assertEqual(self.action.days_until(future_date), 20)

    def test_days_until_deadline(self):
        # Test default action with no deadline returns none
        self.assertEqual(self.action.days_until_deadline(), None)
        # Test future deadline returns correct number of days
        self.action.deadline = datetime.datetime.now(
            timezone.utc) + datetime.timedelta(days=21)
        self.action.save()
        self.assertEqual(self.action.days_until_deadline(), 20)
        # Test past deadline returns correct number of days
        # (though this really shouldn't get called)
        self.action.deadline = datetime.datetime.now(
            timezone.utc) - datetime.timedelta(days=30)
        self.action.save()
        self.assertEqual(self.action.days_until_deadline(), -31)
        # Test setting never_expires turns it to none
        self.action.never_expires = True
        self.action.save()
        self.assertIsNone(self.action.days_until_deadline())

    def test_close_action_set_to_never_expire(self):
        # Test recent action
        self.action.never_expires = True
        self.action.save()
        self.assertFalse(self.action.close_action())
        # Test old action that would otherwise close
        self.old_action.never_expires = True
        self.old_action.save()
        self.assertFalse(self.old_action.close_action())

    def test_close_action_with_deadline_in_past(self):
        self.action.deadline = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=21)
        self.action.save()
        self.assertTrue(self.action.close_action())

    def test_close_action_with_deadline_in_future(self):
        self.action.deadline = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=21)
        self.action.save()
        self.assertFalse(self.action.close_action())

    def test_close_action_with_no_deadline(self):
        self.assertTrue(self.old_action.close_action())
        self.assertFalse(self.action.close_action())

    def test_close_action_with_no_deadline_after_keep_open(self):
        self.old_action.keep_action_open()
        self.assertFalse(self.old_action.close_action())

    def test_send_warning(self):
        # Setup
        days_back = DEFAULT_ACTION_DURATION - DAYS_WARNING_BEFORE_CLOSURE
        warning_date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=days_back-1)
        warning_action = action_factories.Action(date_created=warning_date)
        # Send warning if no deadline set
        self.assertIsNone(warning_action.deadline)
        self.assertTrue(warning_action.send_warning())
        # Don't send if no deadline set
        warning_action.deadline = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=3)
        warning_action.save()
        self.assertFalse(warning_action.send_warning())

    def test_keep_action_open(self):
        # Confirm initial close date
        initial_close_date = self.closing_soon_action.date_created + datetime.timedelta(days=DEFAULT_ACTION_DURATION)
        self.assertEqual(self.closing_soon_action.close_date.date(), initial_close_date.date())
        # Run keep_action_open() and check new date
        self.closing_soon_action.keep_action_open()
        new_date = datetime.datetime.now(timezone.utc) + datetime.timedelta(days=DEFAULT_ACTION_DURATION)
        self.assertEqual(self.closing_soon_action.close_date.date(), new_date.date())

class TestActionForms(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")

    def test_action_form_privacy_choices(self):
        initial_form = ActionForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[0][1]
        user_privacy = self.buffy.profile.privacy_defaults.get_global_default_display()
        self.assertEqual(form_inherited_privacy, user_privacy)

    def test_action_form_privacy_choices_when_not_default(self):
        self.buffy.profile.privacy_defaults.global_default = PrivacyChoices.sitewide
        self.buffy.profile.privacy_defaults.save()
        initial_form = ActionForm(user=self.buffy, formtype="create")
        form_inherited_privacy = initial_form.fields['privacy'].choices[3][1]
        # This is an issue with the privacy utils
        self.assertEqual(form_inherited_privacy, "Your Default (Currently 'Visible sitewide')")

    def test_action_status_is_hidden_on_create(self):
        initial_form = ActionForm(user=self.buffy, formtype="create")
        self.assertEqual(type(initial_form.fields['status'].widget), HiddenInput)


class TestActionPrivacy(TestCase):
    def setUp(self):
        super(TestActionPrivacy, self).setUp()
        self.buffy = User.objects.create(username="buffysummers")

    def test_concrete_privacy(self):
        action = self.buffy.action_set.create(privacy=PrivacyChoices.follows)
        self.assertEqual(action.privacy, PrivacyChoices.follows)
        self.assertEqual(action.current_privacy, PrivacyChoices.follows)

    def test_inherit_privacy(self):
        action = self.buffy.action_set.create(privacy=PrivacyChoices.inherit)
        self.assertEqual(action.privacy, PrivacyChoices.inherit)
        self.assertEqual(action.current_privacy, PrivacyChoices.public)

    def test_update_to_inherit_privacy(self):
        action = self.buffy.action_set.create(privacy=PrivacyChoices.follows)
        self.assertEqual(action.privacy, PrivacyChoices.follows)

        action.privacy = PrivacyChoices.inherit
        action.save()

        self.assertEqual(action.privacy, PrivacyChoices.inherit)
        self.assertEqual(action.current_privacy, PrivacyChoices.public)
