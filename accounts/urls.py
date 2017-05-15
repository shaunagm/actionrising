from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AdminPasswordChangeForm

from accounts import views

urlpatterns = [

    # Create accounts/signup
    url(r'sign-up/$', views.SignUpView.as_view(), name='sign-up'),
    url(r'sent/$', views.SentView.as_view(), name='sent-invite'),
    url(r'^confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.confirmation, name='sign-up-confirmation'),
    url(r'^password_set/$', auth_views.password_change, { 'password_change_form': AdminPasswordChangeForm,
        'template_name': 'accounts/password_reset/change.html'}, name='password_set'),

    # Login/logout
    url(r'^login/$', auth_views.login, {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),

    # Change password (while logged in)
    url(r'^password_change/$', auth_views.password_change, {'template_name': 'accounts/password_reset/change.html'},
        name='password_change'),
    url(r'^password/changed/$', views.change_password_redirect, name='password_change_done'),

    # Reset password (generally for users who can't login because they've forgotten password)
    url(r'^password_reset/$', auth_views.password_reset, { 'template_name': 'accounts/password_reset/form.html',
        'html_email_template_name': 'accounts/password_reset/email.html' }, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done,
        { 'template_name': 'accounts/password_reset/done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, { 'template_name': 'accounts/password_reset/confirm.html'},
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {'template_name': 'accounts/password_reset/complete.html'},
        name='password_reset_complete'),

    # Account settings page
    url(r'^settings/$', views.SettingsView.as_view(), name='settings'),

]
