from django.test import TestCase
from django.core import mail

from django.contrib.auth.models import User
from django_comments.models import Comment
from actions.models import Action, ActionType, ActionTopic
from slates.models import Slate, SlateActionRelationship
from profiles.models import Relationship, ProfileActionRelationship
from notifications.lib.notification_handlers import send_daily_actions
from notifications.lib import dailyaction

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

    def setUp(self):
        # Temporarily delete fixture actions + relationships
        for a in Action.objects.all():
            a.delete()
        for rel in Relationship.objects.all():
            rel.delete()
        # 10 actions, 5 by Willow (friend of Buffy), 5 by Faith (not friend of Buffy),
        # actions 3, 6 and 9 are "popular" via Drusilla + Anya adding them
        # First four are in Buffy's open actions
        self.buffy = User.objects.create(username="buffysummers", email="buffy@sunnydale.edu")
        self.willow = User.objects.create(username="thewitch", email="willow@covens.us")
        rel = Relationship.objects.create(person_A=self.buffy.profile, person_B=self.willow.profile)
        rel.toggle_following_for_current_profile(self.buffy.profile)
        self.faith = User.objects.create(username="faithlehane", email="faithlehane@gmail.net")
        self.anya = User.objects.create(username="anyanka", email="ihatebunnies@sunnydale.edu")
        self.drusilla = User.objects.create(username="dru", email="dru@gmail.net")
        for i in range(0,10):
            if i % 2 == 0:
                action = Action.objects.create(title="Action" + str(i), creator=self.faith)
                ProfileActionRelationship.objects.create(action=action, profile=self.faith.profile)
            else:
                action = Action.objects.create(title="Action" + str(i), creator=self.willow)
                ProfileActionRelationship.objects.create(action=action, profile=self.willow.profile)
            if i % 3 == 0:
                ProfileActionRelationship.objects.create(action=action, profile=self.anya.profile)
                ProfileActionRelationship.objects.create(action=action, profile=self.drusilla.profile)
            if i < 4:
                ProfileActionRelationship.objects.create(action=action, profile=self.buffy.profile)

    def test_most_popular_actions(self):
        # Make Action3 the single most popular action
        action3 = Action.objects.get(title="Action3")
        ProfileActionRelationship.objects.create(action=action3, profile=self.faith.profile)
        actions = dailyaction.most_popular_actions(n=5)
        self.assertEqual(len(actions), 5)
        self.assertEqual(action3, actions[0]) # First item is action3, pars for Willow, Anya, Dru, Buffy, Faith
        self.assertEqual(actions[1].title, "Action0") # Next is action0, pars for Willow, Anya, Dru, Buffy
        self.assertIn(actions[2].title, ["Action6", "Action9"]) # Next should be 6 or 9, for Willow, Anya, Dru
        self.assertIn(actions[4].title, ["Action1", "Action2"]) # 5th should be action1 (Willow + Buffy) or action2 (Faith + Buffy)

    def test_get_popular_actions_default_settings(self):
        actions = dailyaction.most_popular_actions(n=10)
        results = dailyaction.get_popular_actions(self.buffy, actions)
        self.assertEqual(len(results), 10)

    def test_get_popular_actions_with_changed_settings(self):
        # Set to many
        self.buffy.dailyactionsettings.popular_actions = "many"
        self.buffy.dailyactionsettings.save()
        actions = dailyaction.most_popular_actions(n=10)
        results = dailyaction.get_popular_actions(self.buffy, actions)
        self.assertEqual(len(results), 40)
        # Set to none
        self.buffy.dailyactionsettings.popular_actions = "none"
        self.buffy.dailyactionsettings.save()
        actions = dailyaction.most_popular_actions(n=10)
        results = dailyaction.get_popular_actions(self.buffy, actions)
        self.assertEqual(len(results), 0)

    def test_get_my_own_actions(self):
        results = dailyaction.get_my_own_actions(self.buffy)
        self.assertEqual(len(results), 4)
        self.assertIn("Action0", [action.title for action in results])
        self.assertNotIn("Action5", [action.title for action in results])
        # Set to many
        self.buffy.dailyactionsettings.my_own_actions = "many"
        self.buffy.dailyactionsettings.save()
        results = dailyaction.get_my_own_actions(self.buffy)
        self.assertEqual(len(results), 16)
        # Set to none
        self.buffy.dailyactionsettings.my_own_actions = "none"
        self.buffy.dailyactionsettings.save()
        results = dailyaction.get_my_own_actions(self.buffy)
        self.assertEqual(len(results), 0)

    def test_get_my_friends_actions(self):
        results = dailyaction.get_my_friends_actions(self.buffy)
        self.assertEqual(len(results), 5)
        self.assertIn("Action1", [action.title for action in results])
        self.assertNotIn("Action2", [action.title for action in results])
        # Set to many
        self.buffy.dailyactionsettings.my_friends_actions = "many"
        self.buffy.dailyactionsettings.save()
        results = dailyaction.get_my_friends_actions(self.buffy)
        self.assertEqual(len(results), 20)
        # Set to none
        self.buffy.dailyactionsettings.my_friends_actions = "none"
        self.buffy.dailyactionsettings.save()
        results = dailyaction.get_my_friends_actions(self.buffy)
        self.assertEqual(len(results), 0)

    def test_get_actions_from_sources(self):
        # Default
        popular_actions = dailyaction.most_popular_actions(n=10)
        results = dailyaction.get_actions_from_sources(self.buffy, popular_actions)
        self.assertEqual(len(results), 19)
        # Mess around with the settings
        self.buffy.dailyactionsettings.my_friends_actions = "none"
        self.buffy.dailyactionsettings.popular_actions = "many"
        self.buffy.dailyactionsettings.save()
        results = dailyaction.get_actions_from_sources(self.buffy, popular_actions)
        self.assertEqual(len(results), 44)
        # Mess around some more!!
        self.buffy.dailyactionsettings.my_own_actions = "none"
        self.buffy.dailyactionsettings.my_friends_actions = "none"
        self.buffy.dailyactionsettings.popular_actions = "none"
        self.buffy.dailyactionsettings.save()
        results = dailyaction.get_actions_from_sources(self.buffy, popular_actions)
        self.assertEqual(len(results), 0)

    def test_recent_action_filter(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.recent_action_filter(self.buffy, action))
        self.buffy.dailyactionsettings.add_recently_seen_action(action)
        self.assertFalse(dailyaction.recent_action_filter(self.buffy, action))

    def test_finished_action_filter(self):
        action = Action.objects.first() # Action0 through Action3 are Buffy par objects
        self.assertTrue(dailyaction.finished_action_filter(self.buffy, action))
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=action)
        par.status = "don"
        par.save()
        self.assertFalse(dailyaction.finished_action_filter(self.buffy, action))

    def test_duration_filter(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.duration_filter(self.buffy, action))
        # Change duration of action & add that duration to filter
        action.duration = "C"  # A few hours
        action.save()
        self.buffy.dailyactionsettings.duration_filter = "[u'C']" # This is how the db saves from the form
        self.buffy.dailyactionsettings.save()
        # Should still pass the filter since the user hasn't turned the filter *on
        self.assertTrue(dailyaction.duration_filter(self.buffy, action))
        # Turn filter on
        self.buffy.dailyactionsettings.duration_filter_on = True
        self.buffy.dailyactionsettings.save()
        self.assertFalse(dailyaction.duration_filter(self.buffy, action))

    def test_action_type_filter(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.action_type_filter(self.buffy, action))
        # Create action type and add it to action, then add it to filter
        at = ActionType.objects.create(name="Example Action Type")
        action.actiontypes.add(at)
        save_string = "[u'" + str(at.pk) + "']"
        self.buffy.dailyactionsettings.action_type_filter = save_string # This is how the db saves from the form
        self.buffy.dailyactionsettings.save()
        # Should still pass the filter since the user hasn't turned the filter *on
        self.assertTrue(dailyaction.action_type_filter(self.buffy, action))
        # Turn filter on
        self.buffy.dailyactionsettings.action_type_filter_on = True
        self.buffy.dailyactionsettings.save()
        self.assertFalse(dailyaction.action_type_filter(self.buffy, action))

    def test_action_topic_filter(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.action_topic_filter(self.buffy, action))
        # Create action type and add it to action, then add it to filter
        at = ActionTopic.objects.create(name="Example Action Topic")
        action.topics.add(at)
        save_string = "[u'" + str(at.pk) + "']"
        self.buffy.dailyactionsettings.action_topic_filter = save_string # This is how the db saves from the form
        self.buffy.dailyactionsettings.save()
        # Should still pass the filter since the user hasn't turned the filter *on
        self.assertTrue(dailyaction.action_topic_filter(self.buffy, action))
        # Turn filter on
        self.buffy.dailyactionsettings.action_topic_filter_on = True
        self.buffy.dailyactionsettings.save()
        self.assertFalse(dailyaction.action_topic_filter(self.buffy, action))

    def test_filter_action_when_recently_seen(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.filter_action(self.buffy, action))
        self.buffy.dailyactionsettings.add_recently_seen_action(action)
        self.assertFalse(dailyaction.filter_action(self.buffy, action))

    def test_filter_action_when_par_status_set_to_done(self):
        action = Action.objects.first() # Action0 through Action3 are Buffy par objects
        self.assertTrue(dailyaction.filter_action(self.buffy, action))
        par = ProfileActionRelationship.objects.get(profile=self.buffy.profile, action=action)
        par.status = "don"
        par.save()
        self.assertFalse(dailyaction.filter_action(self.buffy, action))

    def test_filter_action_when_duration_filter(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.filter_action(self.buffy, action))
        # Trigger duration filter
        action.duration = "C"
        action.save()
        self.buffy.dailyactionsettings.duration_filter = "[u'C']" # This is how the db saves from the form
        self.buffy.dailyactionsettings.duration_filter_on = True
        self.buffy.dailyactionsettings.save()
        self.assertFalse(dailyaction.filter_action(self.buffy, action))

    def test_filter_action_when_actiontypes_filter(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.filter_action(self.buffy, action))
        # Trigger action type filter
        at = ActionType.objects.create(name="Example Action Type")
        action.actiontypes.add(at)
        save_string = "[u'" + str(at.pk) + "']"
        self.buffy.dailyactionsettings.action_type_filter = save_string # This is how the db saves from the form
        self.buffy.dailyactionsettings.action_type_filter_on = True
        self.buffy.dailyactionsettings.save()
        self.assertFalse(dailyaction.filter_action(self.buffy, action))

    def test_filter_action_when_actiontopics_filter(self):
        action = Action.objects.first()
        self.assertTrue(dailyaction.filter_action(self.buffy, action))
        # Trigger action topic filter
        at = ActionTopic.objects.create(name="Example Action Topic")
        action.topics.add(at)
        save_string = "[u'" + str(at.pk) + "']"
        self.buffy.dailyactionsettings.action_topic_filter = save_string # This is how the db saves from the form
        self.buffy.dailyactionsettings.action_topic_filter_on = True
        self.buffy.dailyactionsettings.save()
        self.assertFalse(dailyaction.filter_action(self.buffy, action))

    def test_get_action_after_filters(self):
        # This is a bit of effort to write, since it chooses randomly from the existing actions.
        pass

    def test_generate_daily_action(self):
        popular_actions = dailyaction.most_popular_actions(n=10)
        result = dailyaction.generate_daily_action(self.buffy, popular_actions)
        self.assertEqual(type(result), Action)
        self.assertIn(result.pk, self.buffy.dailyactionsettings.get_recently_seen_pks())

    def test_actions_filtered_when_action_status_set_to_done(self):
        for action in Action.objects.all():
            action.status = "don"
            action.save()
        popular_actions = dailyaction.most_popular_actions(n=10)
        result = dailyaction.generate_daily_action(self.buffy, popular_actions)
        self.assertFalse(result)
