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
    url(r'^keep_open/(?P<pk>[-\w]+)$', views.keep_actions_open_view, name='keep_open_action'),
    url(r'^create', views.ActionCreateView.as_view(), name='create_action'),
    url(r'^edit/(?P<slug>[-\w]+)$', views.ActionEditView.as_view(), name='edit_action'),
    url(r'^filter-wizard/$', views.filter_wizard_view, name='action_filter'),
    url(r'^filters/(?P<pk>[-\w]+)$', views.ActionFilterView.as_view(), name='filter'),
    url(r'^filter-status/(?P<pk>[-\w]+)/(?P<save_or_delete>[-\w]+)$', views.filter_save_status,
        name='filter-status'),
    # Redirects
    url(r'^slate/(?P<slug>[-\w]+)$', views.SlateRedirectView.as_view(), name='slate_redirect'),
]
