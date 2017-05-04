from django.conf.urls import url

from plugins.phonescript_plugin import views

urlpatterns = [
    url(r'create/?$', views.PhoneScriptCreateView.as_view(), name='create_phonescript_action'),
    url(r'action/(?P<slug>[-\w]+)/?$', views.PhoneScriptView.as_view(), name='phonescript_action'),
    url(r'action/(?P<slug>[-\w]+)/(?P<lookup>[-\w]+)/?$', views.PhoneScriptView.as_view(),
        name='phonescript_action_with_lookup'),
    url(r'positions/(?P<slug>[-\w]+)/?$', views.LegislatorPositionView.as_view(),
        name='view_phonescript_positions'),
    url(r'positions/(?P<slug>[-\w]+)/edit/?$', views.LegislatorPositionEditView.as_view(),
        name='edit_phonescript_positions'),
    url(r'edit/(?P<slug>[-\w]+)/?$', views.PhoneScriptEditView.as_view(), name='edit_phonescript_action'),
    url(r'mass_edit_position/(?P<slug>[-\w]+)/(?P<partysplit>[-\w]+)/?$', views.mass_position_editor,
        name='mass_edit_position'),
]
