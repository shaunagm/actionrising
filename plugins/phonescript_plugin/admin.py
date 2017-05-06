from django.contrib import admin

from plugins.phonescript_plugin.models import PhoneScript, ScriptMatcher, Legislator

admin.site.register(PhoneScript)
admin.site.register(ScriptMatcher)
admin.site.register(Legislator)
