def get_potential_invitees(groupprofile, user):
    '''Takes a given group and finds potential invitees for a given user.  Eligible
    invitees follow the inviting user and are not already members, nor do they have
    pending invitations or requests already.'''
    follow_filter = lambda rel: rel.target_follows_current_profile(user.profile)
    friends = user.profile.filter_connected_profiles(follow_filter)
    filtered_friends = []
    for friend in friends:
        if groupprofile.hasMember(friend.user):
            continue
        if friend.user.pendingmember_set.filter(group=groupprofile):
            continue
        filtered_friends.append(friend)
    return filtered_friends