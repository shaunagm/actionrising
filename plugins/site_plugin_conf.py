from plugins.location_plugin import location_plugin_conf

# Note: first class plugins may be used as second class plugins, but second
# class plugins cannot be used as first class plugins, as they do not provide a
# default for objects that don't have the plugin enabled.

plugins = [
    {'name': 'location_plugin',
        'enabled': True,
        'conf_dict': location_plugin_conf.PluginConf() }
]
