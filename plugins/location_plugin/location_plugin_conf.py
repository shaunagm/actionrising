from django.forms import CharField, BooleanField
from plugins.location_plugin.models import Location, filter_queryset_by_location
from plugins.location_plugin.forms import FilterWizard_Location
from django.contrib.contenttypes.models import ContentType

location_help_text = "Enter the location to help people filter by state and congressional district."
location_help_text_profile = "Enter your location to help us filter state and congressional district."
hide_location_help_text = "Keep your location private, but use it to filter actions."

class PluginConf(object):

    name = "location_plugin"

    templates = {
        "action_instance": "location_plugin/location_for_object.html",
        "profile_instance": "location_plugin/location_for_profile.html",
        "slate_instance": "location_plugin/location_for_object.html",
        "action_controls": "location_plugin/location_control_include.html",
        "action_header_hidden": "location_plugin/hidden_header.html",
        "action_row_hidden": "location_plugin/hidden_row.html"
        }

    form_fields = {
        "ActionForm": { 'location': CharField(help_text=location_help_text, required=False) },
        "SlateForm": { 'location': CharField(help_text=location_help_text, required=False) },
        "ProfileForm": {
            'location': CharField(help_text=location_help_text_profile, required=False),
            'hide_location': BooleanField(required=False, help_text=hide_location_help_text)
            }
        }

    forms = {
        "FilterForm": FilterWizard_Location
    }

    def get_template(self, key):
        return self.templates[key]

    def get_fields(self, form):
        return self.form_fields[str(form.__class__.__name__)]

    def get_plugin_object(self, instance):
        ctype = ContentType.objects.get_for_model(instance)
        return Location.objects.filter(content_type=ctype, object_id=instance.pk).first()

    def create_plugin_object(self, instance):
        ctype = ContentType.objects.get_for_model(instance)
        return Location.objects.create(content_type=ctype, object_id=instance.pk)

    def get_or_create_plugin_object(self, form, instance):
        if hasattr(form, "location_object"):
            return form.location_object
        else:
            return self.create_plugin_object(instance)

    def add_plugin_fields(self, form):
        fields = self.get_fields(form)
        form.fields.update(fields)
        return form

    def add_plugin_field_data(self, form):
        if hasattr(form, "location_object") and form.location_object:
            for field in self.get_fields(form):
                form.fields[field].initial = getattr(form.location_object, field)
        return form

    def add_non_field_data(self, form):
        if form.instance.pk: # If we're updating rather than creating
            form.location_object = self.get_plugin_object(form.instance)
        return form

    def process_plugin_fields(self, form, instance):
        location_object = self.get_or_create_plugin_object(form, instance)
        if location_object:
            for field in self.get_fields(form):
                setattr(location_object, field, form.cleaned_data[field])
            location_object.save()

    def get_filter_form(self, request):
        form = self.forms["FilterForm"]
        return form(request)

    def filter_queryset(self, field_data, queryset, user):
        return filter_queryset_by_location(field_data, queryset, user)

    def get_filter_string(self, filter):
        data = filter.get_plugin_field("location_plugin")
        if data:
            return "Locations of actions: " + ", ".join(data)
