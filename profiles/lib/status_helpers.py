def close_pars_when_action_closes(action):
    '''If action is closed, closes PARs that active, and delete suggested actions'''
    from profiles.models import ProfileActionRelationship
    pars = ProfileActionRelationship.objects.filter(action=action)
    for par in pars:
        if par.status == "ace":
            par.status = "clo"
            par.save()
        if par.status == "sug":
            par.delete()

def open_pars_when_action_reopens(action):
    '''If action is reopened, reopens active PARs that were closed'''
    from profiles.models import ProfileActionRelationship
    pars = ProfileActionRelationship.objects.filter(action=action)
    for par in pars:
        if par.status == "clo":
            par.status = "ace"
            par.save()

def close_commitment_when_PAR_is_closed(par):
    '''If commitment active or waiting, close when par is closed.  If completed,
     expired or already set to removed, don't change anything.'''
    c = Commitment.objects.filter(action=instance.action, profile=instance.profile).first()
    if c.status in ["waiting", "active"]:
        c.status = "removed"
        c.save()

def reopen_commitment_when_par_is_reopened(par):
    '''If commitment was removed, reopen it and decide if it's active/waiting/expired.'''
    c = Commitment.objects.filter(action=instance.action, profile=instance.profile).first()
    if c.status == "removed":
        c.reopen()
