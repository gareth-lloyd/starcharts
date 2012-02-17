from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def home_page(request):
    if (request.user.is_authenticated()):
        return HttpResponseRedirect('/charts/')
    else:
        return render_to_response('base.html')