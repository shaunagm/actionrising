from django.test import TestCase

from django.contrib.auth.models import User
from actions.models import Action, Slate
from mysite.lib.utils import get_content_object

from flags.models import Flag
from flags.lib import flag_helpers

class TestFlagLib(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.slate = Slate.objects.create(title="Test Slate", creator=self.buffy)

    def test_is_flagged_by_user(self):
        # Test that we start with no flags
        action_flag = flag_helpers.is_flagged_by_user(self.action, self.buffy)
        self.assertIsNone(action_flag)
        slate_flag = flag_helpers.is_flagged_by_user(self.slate, self.buffy)
        self.assertIsNone(slate_flag)
        # Add flags
        action_content_object = get_content_object("action", self.action.pk)
        flag = Flag.objects.create(content_object=action_content_object, flagged_by=self.buffy,
            flag_choice="wrong")
        slate_content_object = get_content_object("slate", self.slate.pk)
        flag = Flag.objects.create(content_object=slate_content_object, flagged_by=self.buffy,
            flag_choice="wrong")
        # Try again
        action_flag = flag_helpers.is_flagged_by_user(self.action, self.buffy)
        self.assertTrue(action_flag)
        self.assertEqual([action_flag.content_object, action_flag.flagged_by, action_flag.flag_choice],
            [action_content_object, self.buffy, "wrong"])
        slate_flag = flag_helpers.is_flagged_by_user(self.slate, self.buffy)
        self.assertTrue(slate_flag)
        self.assertEqual([slate_flag.content_object, slate_flag.flagged_by, slate_flag.flag_choice],
            [slate_content_object, self.buffy, "wrong"])

    def test_get_user_flag_if_exists(self):
        # No flags, no formatting
        action_flag = flag_helpers.get_user_flag_if_exists(self.action, self.buffy,
            format=False)
        self.assertIsNone(action_flag)
        # No flags, with formatting
        action_flag = flag_helpers.get_user_flag_if_exists(self.action, self.buffy)
        self.assertEquals(action_flag, "No flags")
        # Add a flag
        action_content_object = get_content_object("action", self.action.pk)
        flag = Flag.objects.create(content_object=action_content_object, flagged_by=self.buffy,
            flag_choice="wrong")
        # Flag, with formatting
        action_flag = flag_helpers.get_user_flag_if_exists(self.action, self.buffy)
        self.assertTrue(action_flag)
        self.assertEqual([action_flag.content_object, action_flag.flagged_by, action_flag.flag_choice],
            [action_content_object, self.buffy, "wrong"])
