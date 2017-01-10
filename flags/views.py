from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from mysite.lib.utils import get_content_object

from flags.models import Flag

@login_required
def process_flag(request, pk, model, reason):
    '''Adds flag to object'''
    # TODO: This should probably be an AJAX call and not URL params
    content_object = get_content_object(model, pk)
    Flag.objects.create(content_object=content_object, flagged_by=request.user,
        flag_choice=reason)
    return HttpResponseRedirect(content_object.get_absolute_url())
