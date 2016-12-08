from django.conf.urls import url

from notifications import views

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$',  views.SettingsEditView.as_view(), name='manage_notifications'),
]
