"""myproject2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from bullion import views

admin.site.site_header = 'BullionReserve downloads'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^details-investor/', views.details_investor, name='details_investor'),
    url(r'^details-personal/', views.details_personal, name='details_personal'),
    url(r'^materials/', views.materials, name='materials'),
    url(r'^profile/', views.profile, name='profile'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^password-reset/', include('password_reset.urls')),
    url(r'^$', views.auth_login, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
