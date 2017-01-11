from mysite.lib.choices import INDIVIDUAL_STATUS_CHOICES
from mysite.lib.privacy import filter_list_for_privacy_annotated, filter_list_for_privacy
from profiles.models import ProfileActionRelationship, ProfileSlateRelationship
from slates.models import SlateActionRelationship

STATUS_DISPLAY_DICT = {
    'sug': 'Suggested to them',
    'ace': 'On their to do list',
    'don': 'Action completed',
    'clo': 'Action closed before they did it',
    'wit': 'This should never get used!'}

def get_people_tracking(object):
    if object.get_cname() == "Action":
        trackers = ProfileActionRelationship.objects.filter(action=object).exclude(status="wit")
    else:
        trackers = ProfileSlateRelationship.objects.filter(slate=object)
    return trackers

def get_slate_tracking(object):
    return SlateActionRelationship.objects.filter(action=object).exclude(status="wit")

def get_people_phrase(people_trackers):
    if len(people_trackers) == 1:
        return "1 person"
    else:
        return "%d people" % len(people_trackers)

def get_slate_phrase(slate_trackers):
    if len(slate_trackers) == 1:
        return "1 slate"
    else:
        return "%d slates" % len(slate_trackers)

def get_tracker_list_for_action(trackers, user):
    action_data = {}
    for status in [choice[0] for choice in INDIVIDUAL_STATUS_CHOICES]:
        filtered_trackers = trackers.filter(status=status)
        annotated_list = filter_list_for_privacy_annotated(filtered_trackers, user)
        action_data[status] = {'status_display': STATUS_DISPLAY_DICT[status], 'list': annotated_list }
    return action_data

def get_tracker_list_for_slate(people_trackers, user):
    # Are we checking for anything but privacy here?
    return filter_list_for_privacy_annotated(people_trackers, user)

def get_tracker_data_for_action(action, user):
    people_trackers = get_people_tracking(action)
    slate_trackers = get_slate_tracking(action)
    return {
        'has_people': True if len(people_trackers) > 0 else False,
        'has_slates': True if len(slate_trackers) > 0 else False,
        'people_phrase': get_people_phrase(people_trackers),
        'slate_phrase': get_slate_phrase(slate_trackers),
        'people_tracker_list': get_tracker_list_for_action(people_trackers, user),
        'slate_tracker_list': get_tracker_list_for_action(slate_trackers, user)}

def get_tracker_data_for_slate(slate, user):
    people_trackers = get_people_tracking(slate)
    return {
        'has_people': True if len(people_trackers) > 0 else False,
        'people_phrase': get_people_phrase(people_trackers),
        'people_tracker_list': get_tracker_list_for_slate(people_trackers, user)}
