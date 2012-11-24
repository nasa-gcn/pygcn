Short description of datables_demo (Example application using datatables.net written in Django).

This demo is pretty self-explanatory. It uses only basic django configuration and, we believe, can be easily understood by django-beginners.
(This is not example of prettiest django project:), aim of this project was to expose code we developed recently to use with great datatables plugin).

The directory 'datatables_demo' contains following files and subdirectories:
- README.txt - this file:)
- manage.py - django default file
- settings.py - project settings file, most settings are default, changed were: "DATABASE_*", INSTALLED_APPS, TEMPLATE_DIRS
- urls.py - file with urls-views mappings (you can find urls and mapped views used in application here)
- demo.db - sqlite3 database file, synchronized with models and filled with example data
- countries.sql - sql file used to fill in database
- site_media - directory with static files (.js, .css, images)
- templates - directory with templates used in application
	- base.html - base template where common html is declared (other templates inherit fromm this one)
	- demo - subdir
		- index.html - template used to display '/' page
		- load_once_demo.html - template used to display '/demo/load-once/'. In this template you can find method how we use datatables with 'load once' (no server side) processing.
		- server_side_demo.html -  template used to display '/demo/server-side/'. In this template you can find method how we use datatables with server side processing.
		- json_countries.txt - template used to render json data with countries used in server side demo.
- demo - django app directory
	- models.py - file with models definition. Only one model in this app (Country) is declared.
	- views.py - file with views methods (documented in code). This file contains 4 views used in application.
	- utils.py - pretty important file since it contains code for preapring data for datatable (server-side mode). Actually get_datatables_records is the function that does most of work.


This demo was prepared with:
- Django 1.1
- Python 2.5.4
- datatables 1.5.4
- jquery 1.3.2

All comments and improvement suggestions are welcome!
