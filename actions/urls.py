from django.conf.urls import url

from actions import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^actions/?$', views.ActionListView.as_view(), name='actions'),
    url(r'^find-actions/?$', views.FindActionsLandingView.as_view(), name='find-actions-landing'),
    url(r'^create-actions/?$', views.CreateActionsLandingView.as_view(), name='create-actions-landing'),
    url(r'^public-actions/?$', views.PublicActionListView.as_view(), name='public-actions'),
    url(r'^learn/?$', views.ActionLearnView.as_view(), name='action-learn'),
    url(r'^action/(?P<slug>[-\w]+)$', views.ActionView.as_view(), name='action'),
    url(r'^create', views.ActionCreateView.as_view(), name='create_action'),
    url(r'^edit/(?P<slug>[-\w]+)$', views.ActionEditView.as_view(), name='edit_action'),
    url(r'^filter/$', views.FilterWizard.as_view(), name='action_filter'),
    # Redirects
    url(r'^slate/(?P<slug>[-\w]+)$', views.SlateRedirectView.as_view(), name='slate_redirect'),
]
