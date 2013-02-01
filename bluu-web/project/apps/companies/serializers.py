# -*- coding: utf-8 -*-
from rest_framework import serializers
from accounts.serializers import UserSerializer

from . import models

class CompanySerializer(serializers.ModelSerializer):
    company_bluuuser = serializers.ManyPrimaryKeyRelatedField()

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'contact_name', 'street',
            'city', 'state', 'zip_code', 'country', 'phone', 'email')


class CompanyAccessSerializer(serializers.Serializer):
    user = UserSerializer()
    groups = serializers.Field()


class CompanyAccessGroupsSerializer(serializers.Serializer):
    name = serializers.Field()
