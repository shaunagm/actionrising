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
