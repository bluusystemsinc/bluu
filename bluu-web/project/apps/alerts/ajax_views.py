# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Group
from django.template import Context
from django.utils.decorators import method_decorator
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib import messages

from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.decorators import permission_required_or_403

from grontextual.models import UserObjectGroup

from bluusites.models import BluuSite

from .models import (Alert, UserAlertDevice, UserAlertConfig)


class AlertCfgCreateView(generics.CreateAPIView):
    """
    Set alert for user
    """
    permission_classes = (permissions.IsAuthenticated,)
    model = UserAlertDevice

    def get_site(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        site = self.get_site(pk)
        print request.DATA
        return 1
        form = SiteInvitationForm(request.DATA,
                                     request=request,
                                     site=site)
 
        if form.is_valid():
            group = form.cleaned_data.get('group', None)
            email = form.cleaned_data.get('email', None)
            is_assigned = site.assign_user(request.user, email, group)
            if is_assigned:
                return Response({'email': email,
                                 'group': request.DATA['group']},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': {
                                    'has_access': _('{} already has access'.\
                                                            format(email))}},
                                 status=status.HTTP_400_BAD_REQUEST)

        return Response({'errors': form.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(permission_required_or_403('bluusites.change_bluusite',
                                                 (BluuSite, 'pk', 'pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('bluusites.add_bluusiteaccess',
                                                 (BluuSite, 'pk', 'pk'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(AlertCfgCreateView, self).dispatch(*args, **kwargs)

