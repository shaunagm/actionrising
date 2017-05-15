from django.conf.urls import url

from commitments import views

urlpatterns = [
    url(r'^new/(?P<slug>[-\w]+)/$',  views.NewCommitmentView.as_view(), name='new_commitment'),
    url(r'^edit/(?P<pk>[0-9]+)/$',  views.EditCommitmentView.as_view(), name='edit_commitment'),
    url(r'^delete/(?P<pk>[0-9]+)/$',  views.delete_commitment, name='delete_commitment'),
]
