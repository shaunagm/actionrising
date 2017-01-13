#######################
### Enabled plugins ###
#######################

# Note: first class plugins may be used as second class plugins, but second
# class plugins cannot be used as first class plugins, as they do not provide a
# default for objects that don't have the plugin enabled.

plugins = [{
    'name': 'location_plugin',
    'first_class': True,
    'enabled': True
    }]

# Not actually sure what I'm doing here, could maybe just assume template names
plugin_template_options = {
    "action_instance": "/action_instance_plugin.html"
    "profile_instance": "/profile_instance_plugin.html"
}
