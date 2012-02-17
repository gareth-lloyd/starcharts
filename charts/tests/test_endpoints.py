
from django.test import TestCase
from charts.models import CheckIn, Chart, DataPoint, DataPoint, ChartData
from charts.forms import AddChartForm
from charts import views
from django.contrib.auth.models import User, UserManager
from datetime import datetime, date, timedelta
from django.utils import simplejson
from django.core.urlresolvers import reverse

class EndpointTests(TestCase):
    # fixture sets up user test, password=password
    # with a chart with pk=1 'I wil attend at least 1 meeting per week'
    # and a variable chart with pk=2 'I will eat less than 2100 calories
    # per day'
    fixtures = ['user_test_with_chart']

    @staticmethod
    def _chart_data():
        return {'verb':'newchart', 'noun':'newchart', 'target':2,
                'target_operator': 'L', 'accumulation_period': 'D',
                'continuous': False}

    def test_default_page(self):
        self.client.login(username='test', password='password')
        response = self.client.get(reverse(views.charts))
        self.assertEquals(200, response.status_code)

    def test_add_chart(self):
        self.client.login(username='test', password='password')
        data = self._chart_data()
        response = self.client.post(reverse(views.charts), data=data)
        self.assertEquals(200, response.status_code)
        chart = Chart.objects.get(verb='newchart', noun='newchart')

    def test_get_chart_data_with_empty_chart(self):
        self.assertTrue(self.client.login(username='test', password='password'))
        data = self._chart_data()
        response = self.client.post(reverse(views.charts), data=data)
        response = self.client.get(reverse(views.all_chart_data))
        self.assertEqual(200, response.status_code)

    def test_get_chartdata_json(self):
        self.client.login(username='test', password='password')
        response = self.client.get(reverse(views.chart_data, kwargs={'chart_id':1}),
                                  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        jsonResponse = simplejson.loads(response.content)
        self.assertTrue(jsonResponse.has_key('chartdata'))

    def test_edit_chart(self):
        self.client.login(username='test', password='password')
        data = {'verb':'verb', 'noun':'noun', 'target':3,
                'target_operator': 'L', 'accumulation_period': 'D',
                'variable_achievements': False}
        self.client.post(reverse(views.edit_chart,
                    kwargs={'chart_id': 1}), follow=True, data=data)
        chart = Chart.objects.get(verb='verb', noun='noun')
        self.assertEquals(3, chart.target)

    def test_add_checkin_to_variable_chart(self):
        self.client.login(username='test', password='password')
        data = {'number': 3}
        response = self.client.post(reverse(views.add_checkin_to_chart,
                    kwargs={'chart_id':2}), data=data)
        self.assertEqual(200, response.status_code)
        num_chkns_after = len(CheckIn.objects.filter(chart__id=2))
        self.assertEquals(1, num_chkns_after)

    def test_add_checkin_to_variable_chart_invalid(self):
        num_chkns = len(CheckIn.objects.filter(chart__id=2))
        self.client.login(username='test', password='password')
        data = {}
        response = self.client.post(reverse(views.add_checkin_to_chart,
                    kwargs={'chart_id':2}), data=data)
        self.assertEqual(400, response.status_code)
        num_chkns_after = len(CheckIn.objects.filter(chart__id=2))
        self.assertEquals(num_chkns, num_chkns_after)

    def test_add_checkin_to_non_variable_chart(self):
        self.client.login(username='test', password='password')
        data={'number': 3}
        response = self.client.post(reverse(views.add_checkin_to_chart,
                    kwargs={'chart_id':1}), data=data)
        checkins = CheckIn.objects.filter(chart__id=1)
        # most recent checkin should have number == 1
        self.assertEqual(1, checkins[len(checkins) - 1].number)

    def test_add_checkin_to_non_variable_chart_invalid(self):
        self.client.login(username='test', password='password')
        data={'number': '<script />'}
        response = self.client.post(reverse(views.add_checkin_to_chart,
                    kwargs={'chart_id':1}), data=data)
        self.assertEqual(400, response.status_code)

    def test_add_retro_checkin(self):
        self.client.login(username='test', password='password')
        data={'number': '100', 'when': '2009-04-26'}
        response = self.client.post(reverse(views.add_checkin_to_chart,
                    kwargs={'chart_id':1}), data=data)
        self.assertEqual(200, response.status_code)
        old_date = date(2009, 4, 26)
        checkin = CheckIn.objects.get(chart__id=1, when=old_date)
        self.assertTrue(checkin != None)

    def test_get_all_chart_data(self):
        self.client.login(username='test', password='password')
        response = self.client.get(reverse(views.all_chart_data),
                                  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        jsonResponse = simplejson.loads(response.content)
        self.assertTrue(jsonResponse.has_key('allChartData'))

    def test_delete_chart(self):
        self.client.login(username='test', password='password')
        self.client.post(reverse(views.delete_chart, kwargs={'chart_id': 1}))
        self.assertEqual(0, len(Chart.objects.filter(pk=1)))

