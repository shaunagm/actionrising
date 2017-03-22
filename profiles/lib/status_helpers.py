from mysite.lib.choices import ToDoStatusChoices

def close_pars_when_action_closes(action):
    '''If action is closed, closes PARs that active, and delete suggested actions'''
    from profiles.models import ProfileActionRelationship
    pars = ProfileActionRelationship.objects.filter(action=action)
    for par in pars:
        if par.status == ToDoStatusChoices.accepted:
            par.status = ToDoStatusChoices.closed
            par.save()
        if par.status == ToDoStatusChoices.suggested:
            par.delete()

def open_pars_when_action_reopens(action):
    '''If action is reopened, reopens active PARs that were closed'''
    from profiles.models import ProfileActionRelationship
    pars = ProfileActionRelationship.objects.filter(action=action)
    for par in pars:
        if par.status == ToDoStatusChoices.closed:
            par.status = ToDoStatusChoices.accepted
            par.save()

def close_commitment_when_PAR_is_closed(par):
    '''If commitment active or waiting, close when par is closed.  If completed,
     expired or already set to removed, don't change anything.'''
    from commitments.models import Commitment
    c = Commitment.objects.filter(action=par.action, profile=par.profile).first()
    if c and c.status in ["waiting", "active"]:
        c.status = "removed"
        c.save()

def reopen_commitment_when_par_is_reopened(par):
    '''If commitment was removed, reopen it and decide if it's active/waiting/expired.'''
    from commitments.models import Commitment
    c = Commitment.objects.filter(action=par.action, profile=par.profile).first()
    if c and c.status == "removed":
        c.reopen()

def close_commitment_when_PAR_is_done(par):
    '''If commitment was removed, reopen it and decide if it's active/waiting/expired.'''
    from commitments.models import Commitment
    c = Commitment.objects.filter(action=par.action, profile=par.profile).first()
    if c and c.status in ["waiting", "active"]:
        c.status = "completed"
        c.save()

def change_commitment_when_par_changes(par, previous_status, current_status):
    if previous_status != ToDoStatusChoices.closed and current_status == ToDoStatusChoices.closed:
        close_commitment_when_PAR_is_closed(par)
    if previous_status != ToDoStatusChoices.accepted and current_status == ToDoStatusChoices.accepted:
        reopen_commitment_when_par_is_reopened(par)
    if previous_status != ToDoStatusChoices.done and current_status == ToDoStatusChoices.done:
        close_commitment_when_PAR_is_done(par)
    # NOTE: This leaves some edge cases - what if a user marks an action as done,
    # then undoes that?  But this is a small minority of use cases which we can come
    # back to.
