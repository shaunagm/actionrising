from django import forms
from django.contrib.contenttypes.models import ContentType
from plugins.location_plugin.models import Location

class FilterWizard_Location(forms.Form):
    question = "What locations should we include?"
    override_template = "location_plugin/filter_wizard.html"

    def __init__(self, request, *args, **kwargs):
        super(FilterWizard_Location, self).__init__(*args, **kwargs)
        ctype = ContentType.objects.get_for_model(request.user.profile)
        location = Location.objects.filter(content_type=ctype, object_id=request.user.profile.pk).first()
        if not location or location.location in ["", None]:
            self.warning = """You do not have a location set, so your selections here
                will be ignored. <br />Why not <a target='_blank' href='%s'>
                    add your location</a> in your profile?""" % request.user.profile.get_edit_url()
        else:
            self.warning = """Your location is set to %s.  If that is incorrect,
                <a target='_blank' href='%s'>you can change it in your profile</a>.""" % (location.location,
                request.user.profile.get_edit_url())

    def update_filter(self, actionfilter, request):
        if 'everything' in request.POST:
            actionfilter.update_plugin_field('location_plugin', ['everything'])
            return
        loc_options = ['District', 'State', 'National']
        selected_loc_options = [option for option in loc_options if option in request.POST]
        actionfilter.update_plugin_field('location_plugin', selected_loc_options)
