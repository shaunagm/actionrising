from mysite.lib.privacy import filter_list_for_privacy_annotated
from mysite.lib.choices import ToDoStatusChoices
from profiles.models import ProfileActionRelationship, ProfileSlateRelationship
from slates.models import SlateActionRelationship
from itertools import groupby
from actions.models import Action
from slates.models import Slate

class Trackers(object):
    def __init__(self, tracked, user):
        self.tracked = tracked
        self.user = user
        _people_tracking = self.get_people_tracking() # don't display
        self.has_people = len(_people_tracking) > 0
        self.people_phrase = self.get_tracker_phrase(len(_people_tracking), 'people')
        if isinstance(self.tracked, Action):
            self.people_tracking_by_status = self.group_by_status_and_privacy(_people_tracking)
            _slates_tracking = self.get_slates_tracking() # don't display
            self.has_slates = len(_slates_tracking) > 0
            self.slates_phrase = self.get_tracker_phrase(len(_slates_tracking), 'slates')
            self.slates_tracking_by_privacy = filter_list_for_privacy_annotated(_slates_tracking, self.user, include_anonymous=True)
        if isinstance(self.tracked, Slate):
            self.people_tracking_by_privacy = filter_list_for_privacy_annotated(_people_tracking, self.user, include_anonymous=True)

    def get_people_tracking(self):
        if self.tracked.get_cname() == "Action":
            trackers = ProfileActionRelationship.objects.filter(action=self.tracked).exclude(status=ToDoStatusChoices.rejected)
        else:
            trackers = ProfileSlateRelationship.objects.filter(slate=self.tracked)
        return trackers

    def get_slates_tracking(self):
        return SlateActionRelationship.objects.filter(action=self.tracked).exclude(status=ToDoStatusChoices.rejected)

    def get_tracker_phrase(self, num_trackers, tracker_type):
        mapping = {
            'people': {'s': 'person', 'pl': 'people'},
            'slates': {'s': 'slate', 'pl': 'slates'}
        }
        number = 's' if num_trackers == 1 else 'pl'
        word = mapping[tracker_type][number]
        return "{0} {1}".format(num_trackers, word)

    def group_by_status_and_privacy(self, trackers):
        keyfunc = lambda tracker: tracker.status
        # sort is a prereq for groupby
        sorted_trackers = sorted(trackers, key = keyfunc)
        grouped_trackers = groupby(sorted_trackers, keyfunc)
        return {status: filter_list_for_privacy_annotated(list(group), self.user, include_anonymous=True)
                for status, group in grouped_trackers}.iteritems
