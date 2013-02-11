# -*- coding: utf-8 -*-
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.parsers import JSONParser
import django_filters
from guardian.shortcuts import get_groups_with_perms, get_objects_for_user

from accounts.models import BluuUser
from companies.models import Company
from companies.serializers import CompanyAccessSerializer,\
        CompanyAccessGroupsSerializer

from .models import BluuSite
from .serializers import SiteSerializer


class SiteFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_type='icontains')
    last_name = django_filters.CharFilter(lookup_type='icontains')
    class Meta:
        model = BluuSite
        fields = ['first_name', 'last_name', 'company']


class SiteList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = BluuSite
    serializer_class = SiteSerializer
    filter_class = SiteFilter

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('accounts.view_site'):
            return super(SiteList, self).get_queryset()
        return get_objects_for_user(user, 'accounts.view_site')


class SiteAccessList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return BluuSite.objects.get(pk=pk)
        except BluuSite.DoesNotExist:
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
            return BluuSite.objects.get(pk=pk)
        except Company.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        site = self.get_object(pk)
        groups = get_groups_with_perms(site)
        sobj = CompanyAccessGroupsSerializer(groups)
        return Response(sobj.data)

