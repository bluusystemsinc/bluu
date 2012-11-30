# -*- coding: utf-8 -*-
from accounts.models import Contract, BluuUser
from accounts.serializers import ContractSerializer, BluuUserSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

class ContractList(APIView):
    """
    List all contracts, or create a new contract.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        contracts = Contract.objects.all()
        serializer = ContractSerializer(contracts)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ContractSerializer(data=request.DATA)
        if serializer.is_valid():
            obj = serializer.save()
            data = serializer.data
            # create initial user
            BluuUser.objects.create(
                username='initial',
                password='initial',
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                contract=obj,
                is_active=True,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)