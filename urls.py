from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from starchart import views
from starchart import settings

admin.autodiscover()

# patterns for contrib modules
urlpatterns = patterns('',
    (r'^accounts/login/$', login, {'template_name': u'login.html'}),
    (r'^accounts/logout/$', logout, {'next_page': '/charts/'}),
    (r'^admin/', include(admin.site.urls)),
)

# starchart urls
urlpatterns += patterns('',
    (r'^$', views.home_page),
    (r'^charts/', include('starchart.charts.urls')),
)

urlpatterns += staticfiles_urlpatterns()
