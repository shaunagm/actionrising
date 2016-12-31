import random
from django.db.models import Count
from actions.models import Action

def most_popular_actions(n=10):
    return Action.objects.filter(status="rea").filter(current_privacy__in=["pub", "sit"]) \
        .annotate(num_trackers=Count('profileactionrelationship')) \
        .order_by('-num_trackers')[:n]

def get_popular_actions(user, popular_actions):
    if user.dailyactionsettings.popular_actions != "none":
        if user.dailyactionsettings.popular_actions == "many":
            popular_actions = list(popular_actions) * 4
        return list(popular_actions)
    return []

def get_my_own_actions(user):
    if user.dailyactionsettings.my_own_actions != "none":
        my_actions = user.profile.get_open_actions()
        if user.dailyactionsettings.my_own_actions == "many":
            my_actions = list(my_actions) * 4
        return list(my_actions)
    return []

def get_my_friends_actions(user):
    if user.dailyactionsettings.my_friends_actions != "none":
        my_friends_actions = user.profile.get_friends_actions()
        if user.dailyactionsettings.my_friends_actions == "many":
            my_friends_actions = list(my_friends_actions) * 4
        return list(my_friends_actions)
    return []

def get_actions_from_sources(user, popular_actions):
    action_draw = []
    action_draw.extend(get_popular_actions(user, popular_actions))
    action_draw.extend(get_my_own_actions(user))
    action_draw.extend(get_my_friends_actions(user))
    return action_draw

def recent_action_filter(user, action):
    if user.dailyactionsettings.recently_seen:
        if action.pk in user.dailyactionsettings.get_recently_seen_pks():
            return
    return action

def duration_filter(user, action):
    if user.dailyactionsettings.duration_filter_on:
        if action.duration in user.dailyactionsettings.get_duration_filter_shortnames():
            return
    return action

def action_type_filter(user, action):
    if user.dailyactionsettings.action_type_filter_on:
        action_type_pks = [i.pk for i in action.actiontypes.all()]
        if set(user.dailyactionsettings.get_type_filter_pks()).intersection(set(action_type_pks)):
            return
    return action

def action_topic_filter(user, action):
    if user.dailyactionsettings.action_topic_filter_on:
        action_topic_pks = [i.pk for i in action.topics.all()]
        if set(user.dailyactionsettings.get_topic_filter_pks()).intersection(set(action_topic_pks)):
            return
    return action

def filter_action(user, action):
    action = recent_action_filter(user, action)
    if action is None: return None
    action = duration_filter(user, action)
    if action is None: return None
    action = action_type_filter(user, action)
    if action is None: return None
    return action_topic_filter(user, action)

def get_action_after_filters(user, actions):
    tries = 0
    while tries < 50:
        action_to_try = random.choice(actions)
        action = filter_action(user, action_to_try)
        if action:
            return action
        else:
            tries += 1
    return None

def generate_daily_action(user, popular_actions):
    actions = get_actions_from_sources(user, popular_actions)
    action = get_action_after_filters(user, actions)
    if action:
        user.dailyactionsettings.add_recently_seen_action(action)
    return action
