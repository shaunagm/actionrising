class PluginConf(object):

    name = "phonescript_plugin"

    def get_views(self, type):
        # Stuck this in a method to prevent circular imports
        from plugins.phonescript_plugin.views import (PhoneScriptView, PhoneScriptEditView,
            PhoneScriptCreateView)
        views = {
            "detail": PhoneScriptView,
            "edit": PhoneScriptEditView,
            "create": PhoneScriptCreateView
        }
        return views[type]
