from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.author_login, name='login'),
    url(r'^logout/$', views.author_logout, name='logout'),
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^unique_name/$', views.unique_name, name='unique_name'),
    url(r'^author/(?P<username>[^\s]+)/$', views.author_entries, name='author_entries'),
    url(r'^entry/(?P<entry_pk>[0-9]+)/$', views.view_entry, name='view_entry'),
    url(r'^add-entry/$', views.add_entry, name='add_entry'),
    url(r'^add-comment/(?P<entry_pk>[0-9]+)/$', views.add_comment, name='add_comment'),
    url(r'^$', views.index, name='index'),
]
