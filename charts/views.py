from datetime import date
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404

from django.template import RequestContext
from django.contrib import messages

from models import Chart, CheckIn, DataPoint, ChartData
from forms import AddCheckInForm, AddChartForm

from django.template.loader import get_template
from django.utils import simplejson
from django.utils.functional import wraps
from django.forms import ValidationError

def return_json(view):
    def wrapper(request, *args, **kwargs):
        try:
            data = view(request, *args, **kwargs)
            status = 200
        except ValidationError as error:
            data = {'error': error.messages}
            status = 400
        json = simplejson.dumps(data, 
                   cls=StarChartJSONEncoder)
        return HttpResponse(json, mimetype='application/json', status=status)
    return wraps(view)(wrapper)

def user_owns_chart(user, chart):
    return user == chart.user

def chart_operation(view):
    """
    decorator to factor out common code around loading charts and
    checking they belong to logged in user
    """
    def wrapper(request, *args, **kwargs):
        if not kwargs.has_key('chart'):
            kwargs['chart'] = get_object_or_404(Chart, id=kwargs['chart_id'])
        if not user_owns_chart(request.user, kwargs['chart']):
            messages.info(request, "You cannot access that chart")
            return HttpResponseRedirect('/')
        return view(request, *args, **kwargs)
    return wraps(view)(wrapper)

@login_required
def charts(request, template_name='charts.html'):
    if request.method == 'POST':
        chart = Chart(user=request.user)
        form = AddChartForm(request.POST, instance=chart)
        if form.is_valid():
            chart = form.save()
            messages.info(request, "Chart saved")
        else:
            messages.info(request, "Invalid chart: %s" % form.errors)
    return render_to_response(template_name, {},
                   RequestContext(request))

@login_required
@return_json
@chart_operation
def edit_chart(request, chart_id=None, chart=None):
    if request.method == 'POST':
        form = AddChartForm(request.POST, instance=chart)
        if form.is_valid():
            chart = form.save()
            success=True
        else:
            success=False
        return {'success': success}

@login_required
@return_json
def all_chart_data(request):
    charts = Chart.objects.filter(user=request.user)
    all_chart_data = [_chart_data(request, chart=chart) for chart in charts]
    return {'allChartData': all_chart_data}

@login_required
@return_json
@chart_operation
def chart_data(request, chart_id=None, chart=None):
    return {'chartdata': _chart_data(request, chart_id, chart)}

def _chart_data(request, chart_id=None, chart=None):
    try:
        num_datapoints = int(request.GET.get('datapoints', 10))
    except ValueError:
        num_datapoints = 10
    return ChartData(chart, num_points=num_datapoints)

@login_required
@chart_operation
def delete_chart(request, chart_id=None, chart=None): 
    if request.method == 'POST':
        chart.delete()
        messages.info(request, "Chart deleted")
    return HttpResponseRedirect('/')

@login_required
@chart_operation
@return_json
def add_checkin_to_chart(request, chart_id=None, chart=None):
    if request.method == 'POST':
        check_in = CheckIn(chart=chart)
        form = AddCheckInForm(request.POST, instance=check_in)
        if form.is_valid():
            check_in.save()
            return {'checkIn': check_in, 
                    'chartData': _chart_data(request, chart=chart)}
        else:
            if form.errors.has_key('number'):
                error_message = form.errors['number']
            else:
                error_message = 'invalid check in'
            raise ValidationError(error_message)
    else:
        return {}

class StarChartJSONEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if isinstance(o, Chart):
            return {
                'id': o.id,
                'verb': o.verb,
                'noun': o.noun,
                'target': o.target,
                'currentProgress': o.get_current(),
                'targetOperator': o.verbose_target_operator(),
                'accumulationPeriod': o.verbose_accumulation_period(),
                'variableAchievements': o.variable_achievements,
            }
        if isinstance(o, CheckIn):
            return {'when': o.when,
                    'start': o.start,
                    'number': o.number}
        elif isinstance(o, DataPoint):
            return {'start': o.start,
                    'number': o.number}
        elif isinstance(o, ChartData):
            return {'datapoints': o.datapoints,
                    'chart': o.chart}
        elif isinstance(o, Chart):
            return o.__unicode__()
        elif isinstance(o, date):
            return o.isoformat()
        else:
            return simplejson.JSONEncoder.default(self, o)
