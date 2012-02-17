from django.conf.urls.defaults import *

from charts import views

# starchart urls
urlpatterns = patterns('',
    (r'^$', views.charts),
    (r'^(?P<chart_id>\d+)/edit/$', views.edit_chart),
    (r'^(?P<chart_id>\d+)/delete/$', views.delete_chart),
    (r'^(?P<chart_id>\d+)/checkins/$', views.add_checkin_to_chart),
    (r'^(?P<chart_id>\d+)/data/$', views.chart_data),
    (r'^data/$', views.all_chart_data),
)
