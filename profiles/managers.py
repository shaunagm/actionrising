from collections import defaultdict
from actstream.managers import ActionManager, stream
from django.contrib.auth.models import User
from django.db.models import prefetch_related_objects
from mysite.lib.privacy import apply_check_privacy
from actions.models import Action
from slates.models import Slate


# TODO:
# - make actor always a profile
# - figure out reverse relationship
# - follow objects instead of searching through them all?


class FilteredManager(ActionManager):

    @stream
    def others(self, model, **kwargs):
        # not my own actions and checking that it is the activity is visible to me

        # exclude my own actions
        me_as_actor = self.actor(model, **kwargs).values_list('id', flat=True)
        me_as_target = self.target(model, **kwargs).values_list('id', flat=True)
        me_as_action_object = self.action_object(model, **kwargs).values_list('id', flat=True)
        my_actions = reduce(set.union, [me_as_action_object, me_as_target, me_as_actor], set())

        feed = self.model_actions(model, **kwargs).exclude(id__in=my_actions)

        objects_by_type = defaultdict(set)
        for act in feed:
            objects_by_type[type(act.actor)].add(act.actor)
            objects_by_type[type(act.target)].add(act.target)
            objects_by_type[type(act.action_object)].add(act.action_object)

        objects_by_type.pop(type(None))

        visible_objects = {None}
        actions = list(objects_by_type[Action])
        prefetch_related_objects(actions, "creator__profile")
        visible_objects.update(apply_check_privacy(actions, model, True))

        slates = list(objects_by_type[Slate])
        prefetch_related_objects(slates, "creator__profile")
        visible_objects.update(apply_check_privacy(slates, model, True))

        users = list(objects_by_type[User])
        prefetch_related_objects(users, "profile")
        visible_objects.update(apply_check_privacy(users, model, True))

        visible_actions = []
        for act in feed:
            for obj in (act.actor, act.target, act.action_object):
                if obj not in visible_objects:
                    print obj, 'not in', visible_objects
                    break
            else:
                visible_actions.append(act.id)

        return self.get_query_set().filter(id__in=visible_actions)
