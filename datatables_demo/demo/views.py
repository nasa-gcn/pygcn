from django.shortcuts import render_to_response
from django.template import RequestContext
from datatables_demo.demo.models import Country
from datatables_demo.demo.utils import get_datatables_records

def index(request):
    return render_to_response('demo/index.html', locals(), context_instance = RequestContext(request))

def load_once_demo_view(request):
    #get all Countries objects. 
    #One thing which is required in 'load once mode' is to somehow prepare list, queryset that can be iterated in
    #given template. Datatables will do the rest. 'countries' is passed in context to template (in this case by using locals())
    countries = Country.objects.all()
    return render_to_response('demo/load_once_demo.html', locals(), context_instance = RequestContext(request))

def server_side_demo_view(request):
    #do not prepare data in view (as in  above view), data will be retrieved using ajax call (see get_countries_list below).
   return render_to_response('demo/server_side_demo.html', locals(), context_instance = RequestContext(request))

def get_countries_list(request):
    #prepare the params

    #initial querySet
    querySet = Country.objects.all()
    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = { 0: 'id', 1 : 'name', 2: 'formal_name', 3: 'capital', 4: 'currency_code', 5: 'currency_name', 6: 'phone_prefix', 7: 'tld' }
    #path to template used to generate json (optional)
    jsonTemplatePath = 'demo/json_countries.txt'

    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath)