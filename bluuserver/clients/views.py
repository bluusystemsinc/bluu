from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from clients.models import Client

# Create your views here.
def showClient(request, client_id):
	p = get_object_or_404(Client, pk=client_id)
	return HttpResponse(p.first_name + ' ' + p.middle_initial + ' ' + p.last_name)
