from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers
from django.utils import simplejson

def get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath = None, *args):
	"""
	Usage: 
		querySet: query set to draw data from.
		columnIndexNameMap: field names in order to be displayed.
		jsonTemplatePath: optional template file to generate custom json from.  If not provided it will generate the data directly from the model.

	"""
	
	cols = int(request.GET.get('iColumns',0)) # Get the number of columns
	iDisplayLength =  min(int(request.GET.get('iDisplayLength',10)),100)	 #Safety measure. If someone messes with iDisplayLength manually, we clip it to the max value of 100.
	startRecord = int(request.GET.get('iDisplayStart',0)) # Where the data starts from (page)
	endRecord = startRecord + iDisplayLength  # where the data ends (end of page)
	
	# Pass sColumns
	keys = columnIndexNameMap.keys()
	keys.sort()
	colitems = [columnIndexNameMap[key] for key in keys]
	sColumns = ",".join(map(str,colitems))
	
	# Ordering data
	iSortingCols =  int(request.GET.get('iSortingCols',0))
	asortingCols = []
		
	if iSortingCols:
		for sortedColIndex in range(0, iSortingCols):
			sortedColID = int(request.GET.get('iSortCol_'+str(sortedColIndex),0))
			if request.GET.get('bSortable_{0}'.format(sortedColID), 'false')  == 'true':  # make sure the column is sortable first
				sortedColName = columnIndexNameMap[sortedColID]
				sortingDirection = request.GET.get('sSortDir_'+str(sortedColIndex), 'asc')
				if sortingDirection == 'desc':
					sortedColName = '-'+sortedColName
				asortingCols.append(sortedColName) 
		querySet = querySet.order_by(*asortingCols)

	# Determine which columns are searchable
	searchableColumns = []
	for col in range(0,cols):
		if request.GET.get('bSearchable_{0}'.format(col), False) == 'true': searchableColumns.append(columnIndexNameMap[col])

	# Apply filtering by value sent by user
	customSearch = request.GET.get('sSearch', '').encode('utf-8');
	if customSearch != '':
		outputQ = None
		first = True
		for searchableColumn in searchableColumns:
			kwargz = {searchableColumn+"__icontains" : customSearch}
			outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)		
		querySet = querySet.filter(outputQ)

	# Individual column search 
	outputQ = None
	for col in range(0,cols):
		if request.GET.get('sSearch_{0}'.format(col), False) > '' and request.GET.get('bSearchable_{0}'.format(col), False) == 'true':
			kwargz = {columnIndexNameMap[col]+"__icontains" : request.GET['sSearch_{0}'.format(col)]}
			outputQ = outputQ & Q(**kwargz) if outputQ else Q(**kwargz)
	if outputQ: querySet = querySet.filter(outputQ)
		
	iTotalRecords = iTotalDisplayRecords = querySet.count() #count how many records match the final criteria
	querySet = querySet[startRecord:endRecord] #get the slice
	sEcho = int(request.GET.get('sEcho',0)) # required echo response
	
	if jsonTemplatePath:
		jstonString = render_to_string(jsonTemplatePath, locals()) #prepare the JSON with the response, consider using : from django.template.defaultfilters import escapejs
		response = HttpResponse(jstonString, mimetype="application/javascript")
	else:
		aaData = []
		a = querySet.values() 
		for row in a:
			rowkeys = row.keys()
			rowvalues = row.values()
			rowlist = []
			for col in range(0,len(colitems)):
				for idx, val in enumerate(rowkeys):
					if val == colitems[col]:
						rowlist.append(str(rowvalues[idx]))
			aaData.append(rowlist)
		response_dict = {}
		response_dict.update({'aaData':aaData})
		response_dict.update({'sEcho': sEcho, 'iTotalRecords': iTotalRecords, 'iTotalDisplayRecords':iTotalDisplayRecords, 'sColumns':sColumns})
		response =  HttpResponse(simplejson.dumps(response_dict), mimetype='application/javascript')
	#prevent from caching datatables result
	add_never_cache_headers(response)
	return response