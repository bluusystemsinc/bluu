# -*- coding: utf-8 -*-
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from guardian.shortcuts import get_groups_with_perms, get_objects_for_user
import django_filters
from accounts.models import BluuUser
from bluusites.api_views import SiteFilter
from bluusites.models import BluuSite
from bluusites.serializers import SiteSerializer
from .models import Company
from .serializers import CompanySerializer,\
        CompanyAccessSerializer, CompanyAccessGroupsSerializer


class CompanySiteList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = BluuSite
    serializer_class = SiteSerializer
    filter_class = SiteFilter

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('accounts.view_site'):
            return super(CompanySiteList, self).get_queryset()
        return get_objects_for_user(user, 'accounts.view_site')

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

