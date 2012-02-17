from django.test import TestCase
from charts.models import CheckIn, Chart, DataPoint, DataPoint, ChartData, TRACKING
from charts.forms import AddChartForm
from charts import views
from django.contrib.auth.models import User, UserManager
from datetime import datetime, date, timedelta
from django.utils import simplejson
from django.core.urlresolvers import reverse

def datapoints_total(datapoints):
    return sum(map(lambda d: d.number, datapoints))

class ChartTest(TestCase):
    fixtures = ['chartdata_setup']

    def setUp(self):
        self.user = User.objects.all()[0]
        self.discrete_chart = Chart.objects.get(pk=1)
        self.variable_chart = Chart.objects.get(pk=2)
        self.tracking_chart = Chart.objects.get(pk=3)

    def test_get_current(self):
        #should be included in total:
        CheckIn.objects.create(number=6, chart=self.variable_chart)
        CheckIn.objects.create(number=6, chart=self.variable_chart)

        #should not be included in total:
        before_period = datetime.now()- timedelta(8)
        CheckIn.objects.create(number=6, chart=self.variable_chart,
                 when=before_period)
        self.failUnlessEqual(self.variable_chart.get_current(), 12)

    def test_get_current_tracking(self):
        "get current returns last checking total"
        now = datetime.now()
        CheckIn.objects.create(number=6, chart=self.tracking_chart,
                              when=now-timedelta(3))
        CheckIn.objects.create(number=7, chart=self.tracking_chart,
                              when=now-timedelta(2))
        CheckIn.objects.create(number=8, chart=self.tracking_chart,
                              when=now-timedelta(1))
        self.failUnlessEqual(self.tracking_chart.get_current(), 8)

class AddChartFormTests(TestCase):
    def test_chart_types_validity(self):
        chart = AddChartForm({'noun': 'highs', 'verb': 'fived',
             'accumulation_period': 'W'})
        self.assertTrue(chart.is_valid())

        chart = AddChartForm({'noun': 'highs', 'verb': 'fived',
              'variable_achievements': False, 'accumulation_period': 'W'})
        self.assertTrue(chart.is_valid())

        chart = AddChartForm({'noun': 'highs', 'verb': 'fived',
              'variable_achievements': True, 'accumulation_period': 'W',
              'target':2, 'target_operator': 'L'})

    def test_instantiation_target_operator_without_target_fails(self):
        form = AddChartForm({'noun': 'yards', 'target_operator': 'L',
                 'verb': 'hobbled'})
        self.assertFalse(form.is_valid())

class ChartDataTests(TestCase):
    fixtures = ['chartdata_setup']

    def add_checkin(self, chart, number, c_date):
        CheckIn(number=number, chart=chart, when=c_date).save()

    def test_chartdata_start_end_next_previous(self):
        now = date.today()
        chart = Chart.objects.get(pk=2)
        self.add_checkin(chart, 5, now);
        self.add_checkin(chart, 5, now - timedelta(5));
        self.add_checkin(chart, 5, now - timedelta(7));

        ChartData(chart, num_points=10)

    def test_fill_up_datapoints(self):
        chart = Chart.objects.get(pk=2)

        now = date.today()
        c0 = CheckIn(number=5, chart=chart, when=now)
        c0.save()
        c1 = CheckIn(number=6, chart=chart, when=(now - timedelta(5)))
        c1.save()
        c2 = CheckIn(number=6, chart=chart, when=(now - timedelta(7)))
        c2.save()

        datapoints = ChartData(chart, num_points=10).datapoints
        self.failUnlessEqual(len(datapoints), 7)
        self.failUnlessEqual(17.0, datapoints_total(datapoints))

    def test_empty_chart(self):
        chart = Chart.objects.get(pk=2)
        cd = ChartData(chart, num_points=10)
        self.failUnlessEqual([], cd.datapoints)

class DataPointTest(TestCase):

    def test_data_point_date_behaviour(self):
        start_date = date(2010, 12, 17)
        adp = DataPoint(start=start_date, accumulation_period="D")
        self.failUnlessEqual(start_date, adp.end)

    def test_datapoint_add_checkin(self):
        when = date(2010, 10, 10)
        c = CheckIn(number=10, when=when)
        adp = DataPoint(start=when, accumulation_period="D")
        adp.add_checkin(c)
        self.failUnlessEqual(10, adp.number)

    def test_datapoint_add_checkin_outside_period(self):
        when = date(2010, 10, 10)
        c = CheckIn(number=10, when=when)
        adp = DataPoint(start=when - timedelta(1), accumulation_period="D")
        adp.add_checkin(c)
        self.failUnlessEqual(0, adp.number)

    def test_start_of_period(self):
        year, month, day = 2010, 8, 17
        time = date(year, month, day)
        start_day = date(year, month, day)
        start_week = date(year, month, 16)
        start_month = date(year, month, 1)
        adp = DataPoint()
        self.failUnlessEqual(adp._start_of_period("D",time), start_day)
        self.failUnlessEqual(adp._start_of_period("W",time), start_week)
        self.failUnlessEqual(adp._start_of_period("M",time), start_month)

    def test_end_of_period(self):
        year, month, day = 2010, 8, 17
        start_time = date(year, month, day)
        end_day = date(year, month, day)
        end_week = date(year, month, 22)
        end_month = date(year, month, 31)

        self.failUnlessEqual(DataPoint(start=start_time, accumulation_period="D")._end_from_start(), end_day)
        self.failUnlessEqual(DataPoint(start=start_time, accumulation_period="W")._end_from_start(), end_week)
        self.failUnlessEqual(DataPoint(start=start_time, accumulation_period="M")._end_from_start(), end_month)

class CheckInTest(TestCase):
    def test_checkin_at_midnight(self):
        date_midnight = date(2010, 10, 12)
        c = CheckIn(number=10, when=date_midnight)
        dp = DataPoint(start=date_midnight, accumulation_period="D");
        dp.add_checkin(c)
        self.failUnlessEqual(10, dp.number)


