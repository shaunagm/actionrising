from plugins.location_plugin import location_plugin_conf
from plugins.phonescript_plugin import phonescript_plugin_conf

field_plugins = [
    {'name': 'location_plugin',
        'enabled': True,
        'conf_dict': location_plugin_conf.PluginConf() }
    ]

special_action_plugins = [
    {'name': 'phonescript_plugin',
        'enabled': True,
        'conf_dict': phonescript_plugin_conf.PluginConf() }
    ]


plugins = field_plugins + special_action_plugins

'''
Notes for docs:
- The plugin's name, x_plugin, must match the url for the detail view
'''
