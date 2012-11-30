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