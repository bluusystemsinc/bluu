from django.db import models

class Client(models.Model):
	COUNTRIES = (
		('US', 'United States of America'),
	)

	first_name = models.CharField(max_length=30)
	middle_initial = models.CharField(max_length=5, null=True)
	last_name = models.CharField(max_length=30)
	site_street_address = models.CharField(max_length=100)
	site_city = models.CharField(max_length=30)
	site_state = models.CharField(max_length=30)
	zip_code = models.CharField(max_length=7)
	site_country = models.CharField(max_length=2, choices=COUNTRIES)
	email_address = models.CharField(max_length=50)
	phone_number = models.CharField(max_length=20)
	serial_number = models.CharField(max_length=20)

