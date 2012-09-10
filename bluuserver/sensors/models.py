from django.db import models
from bluuserver.clients.models import Client

# Create your models here.
class Door(models.Model):
	client = models.ForeignKey(Client, blank=False, null=False, on_delete=models.CASCADE)
	data = models.CharField(max_length=100)

