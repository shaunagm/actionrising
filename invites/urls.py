from django.conf.urls import url

from invites import views

urlpatterns = [
    url(r'request-account$', views.RequestAccountView.as_view(), name='request-account'),
    url(r'^request-confirmation/(?P<slug>[-\w]+)/$', views.request_confirmation_view, name='request-confirmation'),
    url(r'invite-friend$', views.InviteFriendView.as_view(), name='invite-friend'),
    url(r'^invite-confirmation/(?P<slug>[-\w]+)/$', views.invite_confirmation_view, name='invite-confirmation'),
    url(r'sent/$', views.SentView.as_view(), name='sent-invite'),
    url(r'generic_problem/$', views.GenericProblemView.as_view(), name='generic_problem'),

]
