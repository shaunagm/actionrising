from django.conf.urls import url, include

from plugins.phonescript_plugin import views

urlpatterns = [
    url(r'phonescripts', include('plugins.phonescript_plugin.urls')),
]
