from django.conf.urls import url

from flags import views

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/(?P<model>[-\w]+)/(?P<reason>[-\w]+)?$', views.process_flag, name='flag'),
]
