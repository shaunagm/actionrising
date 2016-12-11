from django.test import TestCase
from django.core import mail

from django.contrib.auth.models import User
from django_comments.models import Comment
from actions.models import Action, Slate, SlateActionRelationship
from profiles.models import Relationship, ProfileActionRelationship
from notifications.models import send_daily_actions

###################
### Test models ###
###################

class FollowNotificationTests(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers", email="buffy@sunnydale.edu")
        self.faith = User.objects.create(username="faithlehane")
        self.relationship = Relationship.objects.create(person_A=self.buffy.profile,
            person_B=self.faith.profile)

    def test_follow_email_sent_when_person_followed(self):
        self.assertTrue(self.buffy.notificationsettings.if_followed)
        self.assertFalse(self.relationship.current_profile_follows_target(self.faith.profile))
        self.relationship.toggle_following_for_current_profile(self.faith.profile)
        self.assertTrue(self.relationship.current_profile_follows_target(self.faith.profile))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'faithlehane is now following you on ActionRising')

    def test_follow_email_not_sent_when_person_has_no_email_set(self):
        self.assertTrue(self.buffy.notificationsettings.if_followed)
        self.assertFalse(self.relationship.current_profile_follows_target(self.buffy.profile))
        self.relationship.toggle_following_for_current_profile(self.buffy.profile)
        self.assertTrue(self.relationship.current_profile_follows_target(self.buffy.profile))
        self.assertEqual(len(mail.outbox), 0)

    def test_follow_email_not_sent_when_person_has_turned_notification_setting_off(self):
        self.buffy.notificationsettings.if_followed = False
        self.buffy.notificationsettings.save()
        self.assertFalse(self.buffy.notificationsettings.if_followed)
        self.assertFalse(self.relationship.current_profile_follows_target(self.faith.profile))
        self.relationship.toggle_following_for_current_profile(self.faith.profile)
        self.assertTrue(self.relationship.current_profile_follows_target(self.faith.profile))
        self.assertEqual(len(mail.outbox), 0)

    def test_email_content_is_different_for_mutual_follow(self):
        self.assertFalse(self.relationship.current_profile_follows_target(self.faith.profile))
        self.relationship.toggle_following_for_current_profile(self.faith.profile)
        self.assertTrue(self.relationship.current_profile_follows_target(self.faith.profile))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].body,
            "faithlehaneis following you on ActionRising. You don't follow them, so consider following them back!\n\nTo edit your notification settings, go to 'Your Profile' on www.actionrising.com.")
        # Now faith follows back
        self.faith.email = "faith@sunnydale.edu" # Add Faith's email first
        self.faith.save()
        self.relationship.toggle_following_for_current_profile(self.buffy.profile)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].body,
            "buffysummers is following you on ActionRising. You now follow each other!\n\nTo edit your notification settings, go to 'Your Profile' on www.actionrising.com.")

class TakeActionNotificationTests(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers", email="buffy@sunnydale.edu")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.action2 = Action.objects.create(title="Second Test Action", creator=self.faith)

    def test_takeaction_email_sent_when_person_takes_action(self):
        self.assertTrue(self.buffy.notificationsettings.if_actions_followed)
        ProfileActionRelationship.objects.create(profile=self.faith.profile, action=self.action)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'faithlehane is taking one of your actions on ActionRising')

    def test_takeaction_email_not_sent_when_person_has_no_email_set(self):
        self.assertTrue(self.buffy.notificationsettings.if_actions_followed)
        ProfileActionRelationship.objects.create(profile=self.faith.profile, action=self.action2)
        self.assertEqual(len(mail.outbox), 0)

    def test_takeaction_email_not_sent_when_person_has_turned_notification_setting_off(self):
        self.buffy.notificationsettings.if_actions_followed = False
        self.buffy.notificationsettings.save()
        self.assertFalse(self.buffy.notificationsettings.if_actions_followed)
        ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=self.action)
        self.assertEqual(len(mail.outbox), 0)

class CommentOnActionNotificationTests(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers", email="buffy@sunnydale.edu")
        self.faith = User.objects.create(username="faithlehane")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.action2 = Action.objects.create(title="Second Test Action", creator=self.faith)

    def test_comment_email_sent_when_person_comments(self):
        self.assertTrue(self.buffy.notificationsettings.if_comments_on_my_actions)
        Comment.objects.create(content_object=self.action, user=self.faith,
            site_id=1, comment="This is a comment")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'faithlehane commented on your action on ActionRising')

    def test_comment_email_not_sent_when_person_has_no_email_set(self):
        self.assertTrue(self.buffy.notificationsettings.if_comments_on_my_actions)
        Comment.objects.create(content_object=self.action2, user=self.buffy,
            site_id=1, comment="This is a comment")
        self.assertEqual(len(mail.outbox), 0)

    def test_comment_email_not_sent_when_person_has_turned_notification_setting_off(self):
        self.buffy.notificationsettings.if_comments_on_my_actions = False
        self.buffy.notificationsettings.save()
        self.assertFalse(self.buffy.notificationsettings.if_comments_on_my_actions)
        Comment.objects.create(content_object=self.action, user=self.faith,
            site_id=1, comment="This is a comment")
        self.assertEqual(len(mail.outbox), 0)

class ActionAddedToSlateNotificationTests(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers", email="buffy@sunnydale.edu")
        self.faith = User.objects.create(username="faithlehane")
        self.willow = User.objects.create(username="thewitch")
        self.action = Action.objects.create(title="Test Action", creator=self.buffy)
        self.action2 = Action.objects.create(title="Second Test Action", creator=self.faith)
        self.slate = Slate.objects.create(title="Test Slate", creator=self.willow)

    def test_addtoslate_email_sent_when_action_added_to_slate(self):
        self.assertTrue(self.buffy.notificationsettings.if_my_actions_added_to_slate)
        SlateActionRelationship.objects.create(slate=self.slate, action=self.action)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'thewitch added your action to a slate on ActionRising')

    def test_addtoslate_email_not_sent_when_person_has_no_email_set(self):
        self.assertTrue(self.buffy.notificationsettings.if_my_actions_added_to_slate)
        SlateActionRelationship.objects.create(slate=self.slate, action=self.action2)
        self.assertEqual(len(mail.outbox), 0)

    def test_addtoslate_email_not_sent_when_person_has_turned_notification_setting_off(self):
        self.buffy.notificationsettings.if_my_actions_added_to_slate = False
        self.buffy.notificationsettings.save()
        self.assertFalse(self.buffy.notificationsettings.if_my_actions_added_to_slate)
        SlateActionRelationship.objects.create(slate=self.slate, action=self.action)
        self.assertEqual(len(mail.outbox), 0)

class DailyActionTests(TestCase):

    # Note: This test case is awful, please replace it.

    def create_ten_actions(self, creator, followers):
        for i in range(0,10):
            temp_action = Action.objects.create(title="Action "+ str(i), creator=creator)
            if i % 2:  # Half of the actions have three followers, making them "top" actions
                for follower in followers:
                    ProfileActionRelationship.objects.create(profile=follower.profile, action=temp_action)
        return Action.objects.all()

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers", email="buffy@sunnydale.edu")
        self.faith = User.objects.create(username="faithlehane", email="faith@sunnydale.edu")
        self.kendra = User.objects.create(username="kendra", email="kendra@thevampireslayer.com")
        followers = [User.objects.create(username="dru"), User.objects.create(username="spike"),
            User.objects.create(username="dawn")]
        self.actions = self.create_ten_actions(creator=User.objects.create(username="thewitch"),
            followers=followers)
        # Now we have ten actions, but we still need Buffy and Kendra to add some open actions
        for action in self.actions[:5]:
            ProfileActionRelationship.objects.create(profile=self.buffy.profile, action=action)
            ProfileActionRelationship.objects.create(profile=self.kendra.profile, action=action)
        # Finally, set Kendra to use only popular actions
        self.kendra.notificationsettings.use_own_actions_if_exist = False
        self.kendra.notificationsettings.save()

    def test_daily_actions(self):
        send_daily_actions()
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[0].to, ["buffy@sunnydale.edu"])
        self.assertEqual(mail.outbox[0].body[:62], "Your action for today comes from your personal list of actions")
        self.assertEqual(mail.outbox[1].body[:69], "Your action for today comes from the most popular actions on the site")
        self.assertEqual(mail.outbox[2].body[:69], "Your action for today comes from the most popular actions on the site")
        for index, item in enumerate(mail.outbox):
            action_title = item.body.split("\n\n")[1]
            if index == 0:
                self.assertTrue(action_title in ["Action 0", "Action 1", "Action 2", "Action 3", "Action 4"])
            else:
                self.assertTrue(action_title in ["Action 1", "Action 3", "Action 5", "Action 7", "Action 9"])
