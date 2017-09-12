from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index, name='apartments_all'),
    url(r'^free/$', views.free, name='apartments_free'),
    url(r'^moving-out/$', views.moving_out, name='apartments_moving_out'),
    url(r'^debitors/$', views.debitors, name='apartments_debt'),
    url(r'^renewal-required/$', views.renewal_required, name='apartments_renew'),
    url(r'^renewal-sent/$', views.renewal_sent, name='apartments_update'),
    url(r'^renewal-send-pastdue/$', views.renewal_send_pastdue, name='renewal_send_pastdue'),
    url(r'^renewal-pastdue/$', views.renewal_pastdue, name='renewal_pastdue'),

    url(r'^building/(?P<building_pk>[0-9]+)/$',
        views.building_apartments, name='building_apartments'),

    url(r'^apartments/(?P<apt_pk>[0-9]+)/$',
        views.cc_info, name='contract_info'),
    url(r'^contracts/(?P<contract_id>[0-9]+)/payments/$',
        views.contract_payments, name='contract_payments'),

    url(r'^apartments/(?P<apt_pk>[0-9]+)/send-renewal/$',
        views.send_renewal, name='send-renewal'),
    url(r'^apartments/(?P<apt_pk>[0-9]+)/update-lease/$',
        views.update_lease, name='update_lease'),
    url(r'^apartments/(?P<apt_pk>[0-9]+)/pay-in/$', views.pay_in, name='add_payment'),
    url(r'^apartments/(?P<apt_pk>[0-9]+)/adjust/$', views.rent_adjustment, name='rent_adjustment'),
    url(r'^apartments/(?P<apt_pk>[0-9]+)/start-lease/$',
        views.start_lease, name='start_lease'),
    url(r'^apartments/(?P<apt_pk>[0-9]+)/end-lease/$',
        views.end_lease, name='end_lease'),
    url(r'^apartments/(?P<apt_pk>[0-9]+)/movingout/$', views.set_moving_out_date,
        name='movingout'),

    url(r'^apartments/(?P<apt_pk>[0-9]+)/edit-note/$',
        views.edit_apartment_note, name='edit_apartment_note'),
              
    url(r'^apartments/(?P<apt_pk>[0-9]+)/add-tenant/$',
        views.add_tenant, name='add_tenant'),
    url(r'^tenants/(?P<tenant_id>[0-9]+)/edit/$',
        views.edit_tenant, name='edit_tenant'),
    url(r'^tenants/(?P<tenant_id>[0-9]+)/delete/$',
        views.delete_tenant, name='delete_tenant'),
]
