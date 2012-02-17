from django.test import TestCase
from charts.models import CheckIn, Chart, DataPoint, DataPoint, ChartData, TRACKING
from charts.data import redis, _start_of_period
from charts import views
from django.contrib.auth.models import User, UserManager
from datetime import datetime, date, timedelta
from django.utils import simplejson
from django.core.urlresolvers import reverse

today = date.today()
class DataTest(TestCase):
    fixtures = ['chartdata_setup']

    def setUp(self):
        self.user = User.objects.all()[0]
        # attend at least 1 meeting per week
        self.discrete_chart = Chart.objects.get(pk=1)
        # eat less than 10 cals per day
        self.variable_chart = Chart.objects.get(pk=2)
        # I weighed x kgs
        self.tracking_chart = Chart.objects.get(pk=3)

    def test_chart_with_no_data(self):
        self.assertEquals([], self.discrete_chart.data.all())

    def test_update_discrete_chart_with_continuous_data_fails(self):
        self.assertRaises(ValueError, self.discrete_chart.data.update, 2.5)

    def test_update_chart_defaults_to_today(self):
        self.discrete_chart.data.update(1)
        self.assertEquals(1, self.discrete_chart.data.current)
        self.assertEquals(1, len(self.discrete_chart.data.all()))
        self.assertEquals(today, self.discrete_chart.data.all()[0].when)

    def test_retro_update_fills_backwards(self):
        self.assertEquals(0, len(self.variable_chart.data.all()))

        yesterday = today - timedelta(days=1)
        self.variable_chart.data.update(1, yesterday)

        self.assertEquals(2, len(self.variable_chart.data.all()))
        self.assertEquals(yesterday, self.variable_chart.data.all()[0].when)
        self.assertEquals(today, self.variable_chart.data.all()[1].when)

    def test_current_update_fills_fowards(self):
        chart_data = self.variable_chart.data
        redis.rpush(data.key, '2012-01-27:3')
        self.assertEquals(1, len(chart_data.all()))
        chart_data.update(2.5)
        self.assertEquals(3, len(chart_data.all()))
        self.assertEquals(today, chart_data.all()[-1].when)

    def test_start_of_period(self):
        year, month, day = 2010, 8, 17
        time = date(year, month, day)
        start_day = date(year, month, day)
        start_week = date(year, month, 16)
        start_month = date(year, month, 1)
        self.failUnlessEqual(_start_of_period("D", time), start_day)
        self.failUnlessEqual(_start_of_period(None, time), start_day)
        self.failUnlessEqual(_start_of_period("W", time), start_week)
        self.failUnlessEqual(_start_of_period("M", time), start_month)
