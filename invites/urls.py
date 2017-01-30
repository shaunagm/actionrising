from django.conf.urls import url

from invites import views

urlpatterns = [
    url(r'sign-up$', views.SignUpView.as_view(), name='sign-up'),
    url(r'^sign-up-confirmation/(?P<slug>[-\w]+)/$', views.signup_confirmation_view, name='sign-up-confirmation'),
    url(r'sent/$', views.SentView.as_view(), name='sent-invite'),
    url(r'generic_problem/$', views.GenericProblemView.as_view(), name='generic_problem'),
]
