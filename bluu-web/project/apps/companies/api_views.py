# -*- coding: utf-8 -*-
from django.http import Http404
from django.conf import settings
from django.db.models import Q
from django.template import Context, Template
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import (login_required, permission_required)
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from guardian.shortcuts import get_groups_with_perms, get_objects_for_user
from guardian.decorators import permission_required_or_403
import django_filters
from django_datatables_view.base_datatable_view import BaseDatatableView

from accounts.models import BluuUser
from bluusites.api_views import SiteFilter
from bluusites.models import BluuSite
from bluusites.serializers import SiteSerializer, SitePaginationSerializer
from grontextual.models import UserObjectGroup
from .forms import CompanyInvitationForm
from .models import (Company, CompanyAccess)
from .serializers import CompanySerializer,\
        CompanyAccessSerializer, CompanyAccessGroupsSerializer


class CompanySiteListJson(BaseDatatableView):
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id', 'first_name', 'last_name', 'city']

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        queryset = None
        if self.request.user.has_perm('bluusites.view_bluusite'):
            queryset = BluuSite.objects.all()
        else:
            queryset = BluuSite.objects.filter(company=self.company)
 
        return queryset

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(first_name__istartswith=q) |\
                             Q(last_name__istartswith=q))
        return qs
 
    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        for item in qs:
            json_data.append(
                {
                    "no": no,
                    "first_name": item.first_name,
                    "last_name": item.last_name,
                    "city": item.city,
                    "actions": '<a href="{0}">{1}</a>'.format(reverse('site_edit', args=(item.pk,)), _('Manage'))
                }
            )
            no += 1
        return json_data

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('companies.change_company',
            (Company, 'pk', 'company_pk')))
    @method_decorator(permission_required('bluusites.browse_bluusites'))
    def dispatch(self, *args, **kwargs):
        try:
            self.company = \
                    Company.objects.get(pk=kwargs.get('company_pk', None))
        except Company.DoesNotExist:
            pass
        return super(CompanySiteListJson, self).dispatch(*args, **kwargs)


#class CompanyFilter(django_filters.FilterSet):
#    name = django_filters.CharFilter(lookup_type='icontains')
#    class Meta:
#        model = Company
#        fields = ['name']
#
#
#class CompanyList(generics.ListCreateAPIView):
#    permission_classes = (permissions.IsAuthenticated,)
#    model = Company
#    serializer_class = CompanySerializer
#    filter_class = CompanyFilter
#    filter_fields = ('name',)
#
#    def get_queryset(self):
#        user = self.request.user
#        if user.has_perm('accounts.view_company'):
#            return super(CompanyList, self).get_queryset()
#        return get_objects_for_user(user, 'companies.view_company')
#
#
#class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
#    permission_classes = (permissions.IsAuthenticated,)
#    model = Company
#    serializer_class = CompanySerializer


class CompanyAccessListJson(BaseDatatableView):
    """
    Returns list of users having an access to specified company.
    It's intended to work with Jquery datatable.
    """

    # Defines column names that will be used in sorting.
    # Order is important and should be the same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['email']

    def get_object(self, pk):
        return get_object_or_404(Company, pk=pk)

    def filter_queryset(self, qs):
        q = self.request.GET.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(email__istartswith=q))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        self.company = self.get_object(kwargs.get('company_pk'))

        qs = CompanyAccess.objects.filter(company=self.company)
        # number of records before filtering
        total_records = qs.count()
        qs = self.filter_queryset(qs)
        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)

        # prepare output data
        aaData = self.prepare_results(qs)

        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }

        return ret

    def _render_access_level(self, access):
        """
        Renders cell data determining user's access level to a company.
        Contains links that allow user to change access level. 
        """
        groups = []
        assigned_groups = {}
        if access.invitation:
            assigned_groups[access.group.name] = {"name": access.group.name,
                                               "pk": access.group.pk,
                                               "assigned": True}
        else:
            # if user already has this group
            for uog in UserObjectGroup.objects.get_for_object(access.user, self.company):
                assigned_groups[uog.group.name] = {"name": uog.group.name,
                                                   "pk": uog.group.pk,
                                                   "assigned": True}

        for company_group in settings.COMPANY_GROUPS:
            group = Group.objects.get(name=company_group)
            if group.name not in assigned_groups.keys():
                groups.append({"pk": group.pk, "name": group.name, "assigned": False})
            else:
                groups.append(assigned_groups.get(company_group))

        t = get_template('companies/_company_access_list_cell.html')
        c = Context({
            'access': access,
            'groups': groups})
        return t.render(c)

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        for access in qs:
            rendered_groups = self._render_access_level(access)

            json_data.append(
                {
                    "no": no,
                    "email": access.get_email,
                    "groups": rendered_groups,
                    "invitation": access.invitation,
                    "access": {
                            "id": access.pk,
                            "email": access.get_email,
                            "invitation": access.invitation,
                        }
                }
            )
            no += 1
        return json_data


class CompanyAccessList(generics.ListCreateAPIView):
    """
    Saves access data posted by client.
    """
    permission_classes = (permissions.IsAuthenticated,)
    model = Company

    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404


    def post(self, request, pk, format=None):
        company = self.get_object(pk)
        email = request.DATA['email']
        try:
            user = BluuUser.objects.get(email=email)
        except BluuUser.DoesNotExist:
            user = None
        try:
            if user:
                company_access = CompanyAccess.objects.get(user=user, company=company)
            elif email:
                company_access = CompanyAccess.objects.get(email=email, company=company)

            form = CompanyInvitationForm(request.DATA, instance=company_access, request=request, company=company)
        except CompanyAccess.DoesNotExist:
            form = CompanyInvitationForm(request.DATA, request=request, company=company)
        
        if form.is_valid():
            try:
                user = BluuUser.objects.get(email=email)
                # user exists, so grant him an access to company

                access = form.save(commit=False)
                access.company = company
                access.user = user
                access.save()
                form.save_m2m()

            except BluuUser.DoesNotExist:
                # send invitation
                access = form.save(commit=False)
                access.company = company
                access.invitation = True
                access.save()
                form.save_m2m()

            return Response({'email': request.DATA['email'],
                             'group': request.DATA['group']},
                            status=status.HTTP_201_CREATED)

        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)


class CompanyAccessView(generics.RetrieveUpdateDestroyAPIView):
    model = CompanyAccess

    #def put(self, request, company_pk, pk, format=None):
    #    return super(CompanyAccessView, self).put(request, company_pk, pk, format)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(CompanyAccessView, self).update(request, *args, **kwargs)


class UserGroups:
    def __init__(self, user, groups):
        self.user = user
        self.groups = groups


class CompanyAccessGroups(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        company = self.get_object(pk)
        groups = get_groups_with_perms(company)
        sobj = CompanyAccessGroupsSerializer(groups)
        return Response(sobj.data)

