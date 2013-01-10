# -*- coding: utf-8 -*-
from accounts.models import Site, BluuUser, Company
from accounts.serializers import SiteSerializer, CompanySerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import generics
from rest_framework.renderers import JSONPRenderer, JSONRenderer


class SiteList(APIView):
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


class CompanyList(generics.ListCreateAPIView):
    model = Company
    serializer_class = CompanySerializer


class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Company
    serializer_class = CompanySerializer


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
