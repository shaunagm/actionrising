def is_flagged_by_user(object, user):
    '''Returns flag if object is flagged by user, otherwise none'''
    for flag in object.flags.all():
        if flag.flagged_by == user:
            return flag
    return None

def get_user_flag_if_exists(object, user, format=True):
    flag = is_flagged_by_user(object, user)
    if format and not flag:
        return "No flags"
    return flag
