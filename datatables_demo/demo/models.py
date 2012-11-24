from django.db import models

#this is some model used for demonstartion
class Country(models.Model):
	name = models.CharField(max_length = 32, verbose_name = u'Name')
	formal_name = models.CharField(max_length = 128, verbose_name = u'Formal name', null = True, blank = True)
	capital = models.CharField(max_length = 128, verbose_name = u'Capital', null = True, blank = True)
	currency_code = models.CharField(max_length = 10, verbose_name = u'Currency code', null = True, blank = True)
	currency_name = models.CharField(max_length = 32, verbose_name = u'Currency name', null = True, blank = True)
	phone_prefix = models.CharField(max_length = 16, verbose_name = u'Phone prefix', null = True, blank = True)
	tld = models.CharField(max_length = 16, verbose_name = u'TLD', null = True, blank = True)
	
	def __unicode__(self):
		return self.name