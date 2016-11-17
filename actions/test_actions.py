from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User
from actions.models import Action, Slate, ActionTopic, ActionType
from profiles.models import Profile, ProfileActionRelationship
from actions.views import create_action_helper, create_slate_helper, edit_slate_helper

###################
### Test models ###
###################

class TestActionMethods(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(slug="test-action", creator=self.buffy)
        self.topic = ActionTopic.objects.create(slug="test-topic", name="Test Topic")
        self.actiontype = ActionType.objects.create(slug="test-actiontype", name="Test ActionType")

    def test_get_tags(self):
        self.action.topics.add(self.topic)
        self.action.actiontypes.add(self.actiontype)
        self.assertEqual(self.action.get_tags(), [self.topic, self.actiontype])

    def test_get_creator(self):
        self.assertEqual(self.action.get_creator(), self.buffy)
        self.action.anonymize = True
        self.action.save()
        self.assertEqual(self.action.get_creator(), "Anonymous")

    def test_get_creator_with_link(self):
        self.assertEqual(self.action.get_creator_with_link(),
            "<a href='/profiles/profile/buffysummers'>buffysummers</a>")
        self.action.anonymize = True
        self.action.save()
        self.assertEqual(self.action.get_creator_with_link(), "Anonymous")

class TestActionViews(TestCase):

    def setUp(self):
        self.buffy = User.objects.create(username="buffysummers")
        self.action = Action.objects.create(slug="test-action", creator=self.buffy)
        self.topic = ActionTopic.objects.create(slug="test-topic", name="Test Topic")
        self.actiontype = ActionType.objects.create(slug="test-actiontype", name="Test ActionType")

    def test_create_action_helper(self):
        with self.assertRaises(ObjectDoesNotExist):
            Action.objects.get(slug="test-slug")
        obj = Action(slug="test-slug", title="Test title")
        obj = create_action_helper(obj, [self.actiontype], [self.topic], self.buffy)
        self.assertEqual(obj.creator, self.buffy)
        self.assertEqual(obj.get_tags(), [self.topic, self.actiontype])

    def test_create_slate_helper(self):
        with self.assertRaises(ObjectDoesNotExist):
            Slate.objects.get(slug="test-slug")
        obj = Slate(slug="test-slug", title="Test title")
        obj = create_slate_helper(obj, [self.action], self.buffy)
        self.assertEqual(obj.creator, self.buffy)
        self.assertEqual(list(obj.actions.all()), [self.action])

    def test_edit_slate_helper(self):
        # No actions when create
        obj = Slate.objects.create(slug="test-slug", title="Test title", creator=self.buffy)
        self.assertEqual(list(obj.actions.all()), [])
        # Add some actions via edit_slate_helper
        edit_slate_helper(obj, [self.action])
        self.assertEqual(list(obj.actions.all()), [self.action])
        # Create a new action, and then swap out the actions on the slate
        new_action = Action.objects.create(title="New action", slug="new-slug", creator=self.buffy)
        edit_slate_helper(obj, [new_action])
        self.assertEqual(list(obj.actions.all()), [new_action])
