# -*- coding: utf-8 -*-
from accounts.models import Site, BluuUser, Company
from accounts.serializers import SiteSerializer, CompanySerializer,\
        CompanyAccessSerializer, UserSerializer, CompanyAccessGroupsSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.renderers import JSONPRenderer, JSONRenderer
from rest_framework.parsers import JSONParser

import django_filters
from guardian.shortcuts import get_groups_with_perms, get_objects_for_user


class SiteList_old(APIView):
    """
    List all contracts, or create a new contract.
    """
    #permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        contracts = Site.objects.all()
        serializer = SiteSerializer(contracts)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SiteSerializer(data=request.DATA)
        if serializer.is_valid():
            obj = serializer.save()
            data = serializer.data
            # create initial user
            user = BluuUser.objects.create_user(username='initial',
                                                email=data['email'],
                                                password='initial')
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.contract = obj
            user.is_active = True
            user.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SiteFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_type='icontains')
    last_name = django_filters.CharFilter(lookup_type='icontains')
    class Meta:
        model = Site
        fields = ['first_name', 'last_name', 'company']


class SiteList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Site
    serializer_class = SiteSerializer
    filter_class = SiteFilter

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('accounts.view_site'):
            return super(SiteList, self).get_queryset()
        return get_objects_for_user(user, 'accounts.view_site')


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


class CompanyAccessList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

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
        data = JSONParser().parse(request)
        print 'recived data: ', data
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


class SiteAccessList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Site.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        site = self.get_object(pk)
        groups = get_groups_with_perms(site)
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
        data = JSONParser().parse(request)
        print 'recived data: ', data
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


class SiteAccessGroups(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Site.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        site = self.get_object(pk)
        groups = get_groups_with_perms(site)
        sobj = CompanyAccessGroupsSerializer(groups)
        return Response(sobj.data)







class CompanyList_old(APIView):
    """
    List all companies, or create a new company.
    """
    #permission_classes = (permissions.IsAuthenticated,)
    #renderer_classes = {JSONPRenderer, JSONRenderer}

    def get(self, request, format=None):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CompanySerializer(data=request.DATA)
        if serializer.is_valid():
            obj = serializer.save()
            data = serializer.data

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
