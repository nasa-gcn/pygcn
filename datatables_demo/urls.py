from django.conf.urls.defaults import *
from django.conf import settings
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
	 url(r'^$', 'datatables_demo.demo.views.index'),
     url(r'^demo/load-once/$', 'datatables_demo.demo.views.load_once_demo_view', name = 'load_once_demo'),
	 url(r'^demo/server-side/$', 'datatables_demo.demo.views.server_side_demo_view', name = 'server_side_demo'),

	  url(r'^ajax/get-countries-list/$', 'datatables_demo.demo.views.get_countries_list', name = 'get_countries_list'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

#static files in debug mode(e.g css)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media').replace('\\','/')}),    )