# -*- coding: utf-8 -*-
from django.http import Http404
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import (login_required, permission_required)

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
from .models import Company
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
        if self.request.user.has_perm('accounts.view_site'):
            queryset = BluuSite.objects.all()
        else:
            queryset = get_objects_for_user(self.request.user,
                                            'accounts.view_site')
 
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
                    "city": item.city
                }
            )
            no += 1
        return json_data

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('companies.change_company',
            (Company, 'pk', 'company_pk')))
    @method_decorator(permission_required('accounts.add_bluusite'))
    def dispatch(self, *args, **kwargs):
        try:
            self.company = \
                    Company.objects.get(pk=kwargs.get('company_pk', None))
        except Company.DoesNotExist:
            pass
        return super(CompanySiteListJson, self).dispatch(*args, **kwargs)


class CompanyAccessListJson(BaseDatatableView):
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['id', 'first_name', 'last_name', 'city']

    def get_initial_queryset(self):
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        queryset = None
        if self.request.user.has_perm('accounts.view_site'):
            queryset = BluuSite.objects.all()
        else:
            queryset = get_objects_for_user(self.request.user,\
                                            'accounts.view_site')
 
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
                    "city": item.city
                }
            )
            no += 1
        return json_data



class CompanySiteList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = BluuSite
    serializer_class = SiteSerializer
    paginate_by = 10
    paginate_by_param = 'iDisplayLength'
    pagination_serializer_class = SitePaginationSerializer
    filter_class = SiteFilter
    filter_fields = ('first_name', 'last_name', 'city')

    def get_serializer_context(self):
        context = super(CompanySiteList, self).get_serializer_context()
        queryset = None
        if self.request.user.has_perm('accounts.view_site'):
            queryset = super(CompanySiteList, self).get_queryset()
        else:
            queryset = get_objects_for_user(self.request.user,\
                                            'accounts.view_site')
 
        context['extra'] = {'iTotalRecords': queryset.count()}
        return context

    def _filter_queryset(self, qs):
        q = self.request.QUERY_PARAMS.get('sSearch', None)
        if q is not None:
            return qs.filter(Q(first_name__icontains=q) |\
                             Q(last_name__icontains=q))
        return qs
    
    def _sort_queryset(self, qs):
        """ Get parameters from the request and prepare order by clause
        """
        request = self.request
        # Number of columns that are used in sorting
        try:
            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
        except ValueError:
            i_sorting_cols = 0

        order = []
        order_columns = self.filter_fields
        for i in range(i_sorting_cols):
            # sorting column
            try:
                i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
            except ValueError:
                i_sort_col = 0
            # sorting order
            s_sort_dir = request.REQUEST.get('sSortDir_%s' % i)

            sdir = '-' if s_sort_dir == 'desc' else ''

            sortcol = order_columns[i_sort_col]
            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('%s%s' % (sdir, sc))
            else:
                order.append('%s%s' % (sdir, sortcol))
        if order:
            return qs.order_by(*order)
        return qs

    def get_queryset(self):
        user = self.request.user
        queryset = None
        if user.has_perm('accounts.view_site'):
            queryset = super(CompanySiteList, self).get_queryset()
        else:
            queryset = get_objects_for_user(user, 'accounts.view_site')
        
        queryset = self._filter_queryset(queryset)
        queryset = self._sort_queryset(queryset)
        
        return queryset

    def pre_save(self, obj):
        # pk and/or slug attributes are implicit in the URL.
        company_pk = self.kwargs.get('company', None)
        if company_pk:
            company = Company.objects.get(pk=company_pk)
            setattr(obj, 'company', company)

        if hasattr(obj, 'full_clean'):
            obj.full_clean()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CompanySiteList, self).dispatch(*args, **kwargs)


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    class Meta:
        model = Company
        fields = ['name']


class CompanyList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Company
    serializer_class = CompanySerializer
    filter_class = CompanyFilter
    filter_fields = ('name',)

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('accounts.view_company'):
            return super(CompanyList, self).get_queryset()
        return get_objects_for_user(user, 'accounts.view_company')


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Company
    serializer_class = CompanySerializer


class UserGroups:
    def __init__(self, user, groups):
        self.user = user
        self.groups = groups


class CompanyAccessList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Company

    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        company = self.get_object(pk)
        groups = get_groups_with_perms(company)
        users = BluuUser.objects.filter(groups__in=groups)
        #users = get_users_with_perms(company)
        ret = []
        for user in users:
            user_groups = set(groups) & set(user.groups.all())
            ret.append(UserGroups(user, user_groups))

        sobj = CompanyAccessSerializer(ret)
        return Response(sobj.data)

    def post(self, request, pk, format=None):
        company = self.get_object(pk)
        user = BluuUser.objects.get(email=request.DATA['email'])
        groups = request.DATA['groups']
        group = Group.objects.get(name=groups['name'])
        user.groups.add(group) 


        #TODO:
        # 1. check if user with email exists
        # 2. in doesn't then
        #   2.1 store new user's email and assigned perms
        #   2.2 sent invitation to the user
        #   2.3 after user is registered search accesses looking by email
        #   2.4 assign found permissions to the user
        # 3. set user permissions
        #   3.1 assign permissions to the user
        #   3.2 send invitation to the user

            #return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

