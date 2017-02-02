from site_plugin_conf import plugins


def add_plugin_fields(form):
    for plugin in plugins:
        plugin_object = plugin['conf_dict']
        form = plugin_object.add_plugin_fields(form)
        form = plugin_object.add_non_field_data(form)
        form = plugin_object.add_plugin_field_data(form)
    return form

def process_plugin_fields(form, instance):
    for plugin in plugins:
        plugin_object = plugin['conf_dict']
        form = plugin_object.process_plugin_fields(form, instance)
    return form

def get_filter_forms_for_plugins(request):
    forms = []
    for plugin in plugins:
        plugin_object = plugin['conf_dict']
        forms.append(plugin_object.get_filter_form(request))
    return forms

def run_filters_for_plugins(filter, queryset):
    for plugin in plugins:
        plugin_object = plugin['conf_dict']
        try:
            field_data = filter.get_plugin_field(plugin_object.name)
            queryset = plugin_object.filter_queryset(field_data, queryset, filter.user)
        except:
            pass
    return queryset

def get_plugin_field_strings(filter):
    strings = []
    for plugin in plugins:
        plugin_object = plugin['conf_dict']
        strings.append(plugin_object.get_filter_string(filter))
    return strings
