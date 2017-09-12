from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.index, name='apartments_all'),
    url(r'^format-phone-numbers/$', views.format_phone_numbers, name='format_phone_numbers'),
    url(r'^clear-lease-end/$', views.clear_lease_end, name='clear_lease_end'),
]
