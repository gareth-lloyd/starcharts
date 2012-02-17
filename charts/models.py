from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from calendar import monthrange, isleap

class Chart(models.Model):
    """
    A chart to track something for a particular user.
    """
    TARGET_OPERATORS = (
        ("M", "at least"),
        ("L", "less than"),
        ("E", "exactly"),
    )
    ACCUMULATION_PERIODS = (
        ("D", "day"),
        ("W", "week"),
        ("M", "month"),
    )
    ACHIEVEMENT_TYPES = (
        (False, "It's like attending a meeting - I can either do it or not."),
        (True, "It's like running - I can do different amounts of it."),
    )
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    variable_achievements = models.BooleanField(choices=ACHIEVEMENT_TYPES)
    verb = models.CharField(max_length=50)
    noun = models.CharField(max_length=50)

    target = models.FloatField(blank=True, null=True)
    target_operator = models.CharField(max_length=1,
            choices=TARGET_OPERATORS, null=True, blank=True)
    accumulation_period = models.CharField(max_length=1, choices=ACCUMULATION_PERIODS,
                blank=True, null=True)

    def verbose_accumulation_period(self):
        for period in Chart.ACCUMULATION_PERIODS:
            if self.accumulation_period == period[0]:
                return period[1]
        return ''

    def verbose_target_operator(self):
        for operator in Chart.TARGET_OPERATORS:
            if self.target_operator == operator[0]:
                return operator[1]
        return ''

    def has_target(self):
        return self.target != None and self.target_operator != None

    def get_current(self):
        if not self.accumulation_period:
            try:
                return self.checkin_set.order_by('-when')[0].number
            except IndexError:
                return 0
        else:
            current_period = DataPoint(start=date.today(),
                        accumulation_period=self.accumulation_period)
            checkins = self.checkin_set.filter(when__gte=current_period.start)
            total = 0.0
            for checkin in checkins:
                total += checkin.number
            return total

    def __unicode__(self):
        return "id: %d, variable: %s, accumulation_period: %s, target: %s, target_operator: %s" % (self.id, 
            self.variable_achievements, self.accumulation_period, self.target, self.target_operator)

class ChartData(object):
    def __init__(self, chart, num_points=10, **kwargs):
        self.chart = chart
        self.num_points = num_points

        if chart.accumulation_period:
            self.datapoints = self._get_accumulated_datapoints(chart, num_points)
        else:
            self.datapoints = list(chart.checkin_set.order_by('when'))[-num_points:]

    def _get_accumulated_datapoints(self, chart, num_points):
        accumulation_period = chart.accumulation_period

        datapoints = []
        current_datapoint = DataPoint(start=date.today(), accumulation_period=accumulation_period)
        datapoints.append(current_datapoint)

        for checkin in chart.checkin_set.all().order_by('-when'):
            while checkin.when < current_datapoint.start:
                current_datapoint = current_datapoint.previous()
                datapoints.append(current_datapoint)
            current_datapoint.add_checkin(checkin)
        return list(reversed(datapoints))[-num_points:]


class CheckIn(models.Model):
    """
    One measurement on a particular chart
    """
    number = models.FloatField()
    when = models.DateField(default=date.today())
    created = models.DateTimeField(auto_now_add = True)
    chart = models.ForeignKey(Chart)

    @property
    def start(self):
        return self.when

    @property
    def end(self):
        return self.when

    def __unicode__(self):
        return u'%s at %s' % (self.number, self.when)


class DataPoint(object):
    """
    A meaningful data point
    """
    def __init__(self, start=None, number=0.0, accumulation_period=None):
        self.number = number
        self.accumulation_period = accumulation_period
        self.start = self._start_of_period(accumulation_period, start)
        self.end = self._end_from_start(accumulation_period)

    def previous(self):
        return DataPoint(start=self.start - timedelta(days=1),
                accumulation_period=self.accumulation_period)

    def _start_of_period(self, accumulation_period, date_in_period):
        if accumulation_period == None:
            return None
        if accumulation_period == Chart.ACCUMULATION_PERIODS[0][0]: # daily
            tt = date_in_period.timetuple()
            return date(tt[0], tt[1],tt[2]) 
        elif accumulation_period == Chart.ACCUMULATION_PERIODS[1][0]: # weekly
            first_day = (date_in_period -
                         timedelta(date_in_period.weekday()))
            tt = first_day.timetuple()
            return date(tt[0], tt[1],tt[2]) 
        elif accumulation_period == Chart.ACCUMULATION_PERIODS[2][0]: # monthly
            tt = date_in_period.timetuple()
            return date(tt[0], tt[1], 1) 
        raise ValueError('parameter accumulation_period not a recognized value')

    def _end_from_start(self, accumulation_period):
        """
        get end of period relative to start
        """
        if accumulation_period == None:
            return None
        if accumulation_period == Chart.ACCUMULATION_PERIODS[0][0]: # daily
            return self.start
        elif accumulation_period == Chart.ACCUMULATION_PERIODS[1][0]: # weekly
            return self.start + timedelta(6)
        elif accumulation_period == Chart.ACCUMULATION_PERIODS[2][0]: # monthly
            tt = self.start.timetuple()
            year = tt[0] if tt[1] < 12 else tt[0] + 1
            month = tt[1] + 1 if tt[1] < 12 else 1
            return date(year, month, 1) - timedelta(1)
        raise ValueError('parameter accumulation_period not a recognized value')

    def add_checkin(self, checkin):
        if self.start <= checkin.when <= self.end: 
            self.number += checkin.number

    def __unicode__(self):
        return u'%s from %s (%s)' % (self.total, self.start, self.accumulation_period)
