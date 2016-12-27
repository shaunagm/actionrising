from django.test import TestCase
from django.core import mail

from django.contrib.auth.models import User
from django_comments.models import Comment
from actions.models import Action, Slate, SlateActionRelationship
from profiles.models import Relationship, ProfileActionRelationship
from notifications.lib.notification_handlers import send_daily_actions

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

    # def test_email_content_is_different_for_mutual_follow(self):
    #     self.assertFalse(self.relationship.current_profile_follows_target(self.faith.profile))
    #     self.relationship.toggle_following_for_current_profile(self.faith.profile)
    #     self.assertTrue(self.relationship.current_profile_follows_target(self.faith.profile))
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].body,
    #         "faithlehane is following you on ActionRising. You don't follow them, so consider following them back!\n\nTo edit your notification settings, go to 'Your Profile' on www.actionrising.com.")
    #     # Now faith follows back
    #     self.faith.email = "faith@sunnydale.edu" # Add Faith's email first
    #     self.faith.save()
    #     self.relationship.toggle_following_for_current_profile(self.buffy.profile)
    #     self.assertEqual(len(mail.outbox), 2)
    #     self.assertEqual(mail.outbox[1].body,
    #         "buffysummers is following you on ActionRising. You now follow each other!\n\nTo edit your notification settings, go to 'Your Profile' on www.actionrising.com.")

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
