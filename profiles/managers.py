from collections import defaultdict
from actstream.managers import ActionManager, stream, check
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import prefetch_related_objects, Q
from mysite.lib.privacy import apply_check_privacy
from actions.models import Action
from slates.models import Slate


class FilteredManager(ActionManager):

    @stream
    def not_any(self, obj, **kwargs):
        """ find actions not including this obj
        based on self.any() """

        check(obj)
        ctype = ContentType.objects.get_for_model(obj)

        not_actor = ~Q(actor_content_type=ctype, actor_object_id=obj.pk)
        not_target = ~Q(target_content_type=ctype, target_object_id=obj.pk)
        not_action_object = ~Q(action_object_content_type=ctype, action_object_object_id=obj.pk)

        return self.public(not_actor & not_target & not_action_object, **kwargs)

    @stream
    def others(self, user, **kwargs):
        """ Actions visible to user on objects that are not directly related to the user """

        feed = self.not_any(user)

        # separate objects out by type so we can prefetch relations type-by-type
        objects_by_type = defaultdict(set)
        for act in feed:
            objects_by_type[type(act.actor)].add(act.actor)
            objects_by_type[type(act.target)].add(act.target)
            objects_by_type[type(act.action_object)].add(act.action_object)

        visible_objects = {None}  # visible objects in left in stream

        # apply_check_privacy frequently looks up the owner's profile so we use
        # prefetch_related_objects to pre-lookup the owners profiles for the
        # objects
        actions = list(objects_by_type[Action])
        prefetch_related_objects(actions, "creator__profile")
        visible_objects.update(apply_check_privacy(actions, user, True))

        slates = list(objects_by_type[Slate])
        prefetch_related_objects(slates, "creator__profile")
        visible_objects.update(apply_check_privacy(slates, user, True))

        users = list(objects_by_type[User])
        prefetch_related_objects(users, "profile")
        visible_objects.update(apply_check_privacy(users, user, True))

        visible_actions = [
            act.id for act in feed
            if visible_objects.issuperset({act.actor, act.target, act.action_object})]

        # stream interface expects a queryset so we fetch again
        return self.get_query_set().filter(id__in=visible_actions)
