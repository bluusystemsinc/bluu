# -*- coding: utf-8 -*-
from django.http import Http404
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
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
            #queryset = get_objects_for_user(self.request.user,
            #                                'bluusites.view_bluusite')
 
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
    @method_decorator(permission_required('bluusites.browse_bluusites'))
    def dispatch(self, *args, **kwargs):
        try:
            self.company = \
                    Company.objects.get(pk=kwargs.get('company_pk', None))
        except Company.DoesNotExist:
            pass
        return super(CompanySiteListJson, self).dispatch(*args, **kwargs)


#class CompanySiteList(generics.ListCreateAPIView):
#    permission_classes = (permissions.IsAuthenticated,)
#    model = BluuSite
#    serializer_class = SiteSerializer
#    paginate_by = 10
#    paginate_by_param = 'iDisplayLength'
#    pagination_serializer_class = SitePaginationSerializer
#    filter_class = SiteFilter
#    filter_fields = ('first_name', 'last_name', 'city')
#
#    def get_serializer_context(self):
#        context = super(CompanySiteList, self).get_serializer_context()
#        queryset = None
#        if self.request.user.has_perm('accounts.view_site'):
#            queryset = super(CompanySiteList, self).get_queryset()
#        else:
#            queryset = get_objects_for_user(self.request.user,\
#                                            'accounts.view_site')
# 
#        context['extra'] = {'iTotalRecords': queryset.count()}
#        return context
#
#    def _filter_queryset(self, qs):
#        q = self.request.QUERY_PARAMS.get('sSearch', None)
#        if q is not None:
#            return qs.filter(Q(first_name__icontains=q) |\
#                             Q(last_name__icontains=q))
#        return qs
#    
#    def _sort_queryset(self, qs):
#        """ Get parameters from the request and prepare order by clause
#        """
#        request = self.request
#        # Number of columns that are used in sorting
#        try:
#            i_sorting_cols = int(request.REQUEST.get('iSortingCols', 0))
#        except ValueError:
#            i_sorting_cols = 0
#
#        order = []
#        order_columns = self.filter_fields
#        for i in range(i_sorting_cols):
#            # sorting column
#            try:
#                i_sort_col = int(request.REQUEST.get('iSortCol_%s' % i))
#            except ValueError:
#                i_sort_col = 0
#            # sorting order
#            s_sort_dir = request.REQUEST.get('sSortDir_%s' % i)
#
#            sdir = '-' if s_sort_dir == 'desc' else ''
#
#            sortcol = order_columns[i_sort_col]
#            if isinstance(sortcol, list):
#                for sc in sortcol:
#                    order.append('%s%s' % (sdir, sc))
#            else:
#                order.append('%s%s' % (sdir, sortcol))
#        if order:
#            return qs.order_by(*order)
#        return qs
#
#    def get_queryset(self):
#        user = self.request.user
#        queryset = None
#        if user.has_perm('accounts.view_site'):
#            queryset = super(CompanySiteList, self).get_queryset()
#        else:
#            queryset = get_objects_for_user(user, 'accounts.view_site')
#        
#        queryset = self._filter_queryset(queryset)
#        queryset = self._sort_queryset(queryset)
#        
#        return queryset
#
#    def pre_save(self, obj):
#        # pk and/or slug attributes are implicit in the URL.
#        company_pk = self.kwargs.get('company', None)
#        if company_pk:
#            company = Company.objects.get(pk=company_pk)
#            setattr(obj, 'company', company)
#
#        if hasattr(obj, 'full_clean'):
#            obj.full_clean()
#
#    def create(self, request, *args, **kwargs):
#        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
#
#        if serializer.is_valid():
#            self.pre_save(serializer.object)
#            self.object = serializer.save()
#            headers = self.get_success_headers(serializer.data)
#            return Response(serializer.data, status=status.HTTP_201_CREATED,
#                            headers=headers)
#
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#    @method_decorator(csrf_exempt)
#    def dispatch(self, *args, **kwargs):
#        return super(CompanySiteList, self).dispatch(*args, **kwargs)


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



class CompanyAccessListJson(BaseDatatableView):
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['', 'email']

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
        #qs = self.get_initial_queryset()
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

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []

        try:
            no = int(self.request.GET.get('iDisplayStart', 0)) + 1
        except (ValueError, TypeError):
            no = 0

        for access in qs:
            if access.invitation:
                groups = [{"pk": access.group.pk, "name": access.group.name + ' (pending)'}]
            else:
                groups = [{"pk": uog.group.pk, "name": uog.group.name} for uog in UserObjectGroup.objects.get_for_object(access.user, self.company)]
            json_data.append(
                {
                    "no": no,
                    "email": access.get_email,
                    "groups": groups,
                    "invitation": access.invitation
                }
            )
            no += 1
        return json_data


#    def post(self, request, company_pk, format=None):
#        self.company = self.get_object(company_pk)
#        form = CompanyInvitationForm(request.POST)
#        
#        if form.is_valid():
#            try:
#                user = BluuUser.objects.get(email=request.DATA['email'])
#                # user exists, so grant him an access to company
#
#                #group = request.DATA['group']
#                #group = Group.objects.get(pk=group)
#
#                access = form.save(commit=False)
#                access.user = user
#                access.save()
#                form.save_m2m()
#
#                #CompanyAccess.objects.create(company=company, user=user)
#                # assign the group to the user in the context of company
#                UserObjectGroup.objects.assign(group, user, company)
#            except BluuUser.DoesNotExist:
#                # send invitation
#                access = form.save(commit=False)
#                access.invitation = True
#                access.save()
#                form.save_m2m()
#
#            return Response({'email': request.DATA['email'],
#                             'group': request.DATA['group']},
#                            status=status.HTTP_201_CREATED)
#
#        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyAccessList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Company

    def get_object(self, pk):
        try:
            return Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

#    def get(self, request, pk, format=None):
#        company = self.get_object(pk)
#        groups = get_groups_with_perms(company)
#        users = BluuUser.objects.filter(groups__in=groups)
#        #users = get_users_with_perms(company)
#        ret = []
#        for user in users:
#            user_groups = set(groups) & set(user.groups.all())
#            ret.append(UserGroups(user, user_groups))
#
#        sobj = CompanyAccessSerializer(ret)
#        return Response(sobj.data)

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

                # assign the group to the user in the context of company
                UserObjectGroup.objects.assign(access.group, user, company)
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

