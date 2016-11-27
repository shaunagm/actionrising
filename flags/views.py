from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

from flags.models import Flag

@login_required
def process_flag(request, pk, model, reason):
    """ This should probably be an AJAX call and not URL parms """
    if model.lower() in ["action", "slate"]:
        app_label = "actions"
    else:
        app_label = "profiles"
    ct = ContentType.objects.get(app_label=app_label, model=model.lower())
    content_object = ct.get_object_for_this_type(pk=pk)
    Flag.objects.create(content_object=content_object, flagged_by=request.user, flag_choice=reason)
    return HttpResponseRedirect(content_object.get_absolute_url())
