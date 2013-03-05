# -*- coding: utf-8 -*-
import math

from django.http import Http404
from django.conf import settings
from django.db.models import Q
from django.template import Context
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from guardian.shortcuts import get_groups_with_perms, get_objects_for_user
from guardian.decorators import permission_required, permission_required_or_403
import django_filters
from django_datatables_view.base_datatable_view import BaseDatatableView

from accounts.models import BluuUser
from grontextual.models import UserObjectGroup
from invitations.models import InvitationKey
from .forms import CompanyInvitationForm
from .models import (Company, CompanyAccess)


class CompanySiteListJson(BaseDatatableView):
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id', 'first_name', 'last_name', 'city']

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        queryset = self.request.user.get_sites()
        return queryset.filter(company=self.company)

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

    @method_decorator(permission_required_or_403('companies.change_company',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('bluusites.browse_bluusites',
                                                 accept_global_perms=True))
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


class CompanyAccessListCreateView(generics.ListCreateAPIView):
    model = CompanyAccess
    paginate_by = 20
    paginate_by_param = 'iDisplayLength'
  
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        self.object_list = self.filter_queryset(queryset)

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        allow_empty = self.get_allow_empty()
        if not allow_empty and not self.object_list:
            class_name = self.__class__.__name__
            error_msg = self.empty_error % {'class_name': class_name}
            raise Http404(error_msg)
        # Pagination size is set by the `.paginate_by` attribute,
        # which may be `None` to disable pagination.
        page_size = self.get_paginate_by(self.object_list)
        if page_size:
            packed = self.paginate_queryset(self.object_list, page_size)
            paginator, page, queryset, is_paginated = packed
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)
        
        data = {
                'sEcho': request.GET.get('sEcho', 1),
                'iTotalRecords': serializer.data['count'],
                'iTotalDisplayRecords': serializer.data['count'],
                'aaData': serializer.data['results']
                
        }
        return Response(data)


    @csrf_exempt
    @method_decorator(permission_required_or_403('companies.change_company',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('companies.browse_companyaccessess',
                                                 accept_global_perms=True))
    def dispatch(self, request, *args, **kwargs):
        request.GET = request.GET.copy()
        page_size = request.GET.get('iDisplayLength', 10)
        object_number = request.GET.get('iDisplayStart', 1)

        if (page_size == '-1'):
            page_size = request.GET['iDisplayLength'] = 10

        try:
            object_number = float(object_number)
        except ValueError:
            object_number = 1
        try:
            page_size = float(page_size)
        except ValueError:
            page_size = 10

        page = int(math.ceil(object_number / page_size))
        request.GET['page'] = page
        return super(CompanyAccessListCreateView, self).dispatch(request, *args, **kwargs)


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

        ret = {'sEcho': int(request.GET.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }

        return ret

    def _render_access_level(self, access, current_access):
        """
        Renders cell data determining user's access level to a company.
        Contains links that allow user to change access level. 
        """
        groups = []
        assigned_groups = {}
        if access.invitations.filter(registrant__isnull=True).exists():
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
            'current_access': current_access,
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

        try:
            current_access = CompanyAccess.objects.get(user=self.request.user,
                                                       company=self.company)
            current_access_pk = current_access.pk
        except CompanyAccess.DoesNotExist:
            current_access_pk = -1


        for access in qs:
            rendered_groups = self._render_access_level(access,
                                                        current_access_pk)

            json_data.append(
                {
                    "access": {
                        "no": no,
                        "id": access.pk,
                        "email": access.get_email,
                        "groups": rendered_groups,
                        "invitation": access.invitations.filter(registrant__isnull=True).exists(),
                    }
                }
            )
            no += 1
        return json_data

    @method_decorator(permission_required_or_403('companies.change_company',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('companies.browse_companyaccesses',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyAccessListJson, self).dispatch(*args, **kwargs)


class CompanyAccessCreateView(generics.CreateAPIView):
    """
    Create access for user to company
    """
    permission_classes = (permissions.IsAuthenticated,)
    model = Company

    def get_company(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def post(self, request, company_pk, format=None):
        company = self.get_company(company_pk)
        email = request.DATA['email']
        try:
            user = BluuUser.objects.get(email__iexact=email)
            return Response({'errors': {'has_access': _('{} already has access'.format(email))}}, status=status.HTTP_400_BAD_REQUEST)
        except BluuUser.DoesNotExist:
            user = None
        try:
            if user:
                company_access = CompanyAccess.objects.get(user=user,
                                                           company=company)
            elif email:
                company_access = CompanyAccess.objects.get(email__iexact=email,
                                                           company=company)

            form = CompanyInvitationForm(request.DATA,
                                         instance=company_access,
                                         request=request,
                                         company=company)
        except CompanyAccess.DoesNotExist:
            form = CompanyInvitationForm(request.DATA,
                                         request=request,
                                         company=company)
        
        if form.is_valid():
            access = form.save(commit=False)
            access.company = company
            try:
                user = BluuUser.objects.get(email__iexact=email)
                # user exists, so grant him an access to company
                access.user = user
                access.email = user.email  # this is to prevent changing user's email after ca was saved
                access.save()
                form.save_m2m()
            except BluuUser.DoesNotExist:
                # send invitation
                access.save()
                form.save_m2m()
                invitation = InvitationKey.objects.create_invitation(
                        user=request.user,
                        content_object=access
                        )
                invitation.send_to(access.email)

            return Response({'email': email,
                             'group': request.DATA['group']},
                            status=status.HTTP_201_CREATED)

        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(permission_required_or_403('companies.change_company',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('companies.add_companyaccess',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyAccessCreateView, self).dispatch(*args, **kwargs)


class CompanyAccessUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    Change existing access level
    """
    model = CompanyAccess

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(CompanyAccessUpdateView, self).update(request, *args, **kwargs)

    @method_decorator(permission_required_or_403('companies.change_company',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    @method_decorator(permission_required_or_403('companies.change_companyaccess',
                                                 (Company, 'pk', 'company_pk'),
                                                 accept_global_perms=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyAccessUpdateView, self).dispatch(*args, **kwargs)


