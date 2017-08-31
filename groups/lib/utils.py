def get_potential_invitees(groupprofile, user):
    '''Takes a given group and finds potential invitees for a given user.  Eligible
    invitees follow the inviting user and are not already members, nor do they have
    pending invitations or requests already.'''
    follow_filter = lambda rel: rel.target_follows_current_profile(user.profile)
    friends = user.profile.filter_connected_profiles(follow_filter)
    return [friend for friend in friends if not (groupprofile.hasMember(friend.user)
        or friend.user.pendingmember_set.filter(group=groupprofile))]
