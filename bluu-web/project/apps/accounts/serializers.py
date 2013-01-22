# -*- coding: utf-8 -*-
from accounts import models
from django.contrib.auth.models import User
from rest_framework import serializers



class BluuUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BluuUser
        fields = ('url', 'username', 'snippets')


class CompanySerializer(serializers.ModelSerializer):
    company_bluuuser = serializers.ManyPrimaryKeyRelatedField()

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'contact_name', 'street',
            'city', 'state', 'zip_code', 'country', 'phone', 'email')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BluuUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class SiteSerializer(serializers.ModelSerializer):
    contract_bluuuser = serializers.ManyPrimaryKeyRelatedField()
    company = CompanySerializer()

    class Meta:
        model = models.Site
        fields = ('id', 'first_name', 'middle_initial', 'last_name', 'street',
            'city', 'state', 'zip_code', 'country', 'phone', 'email', 'company')


class CompanyAccessSerializer(serializers.Serializer):
    user = UserSerializer()
    groups = serializers.Field()


class CompanyAccessGroupsSerializer(serializers.Serializer):
    name = serializers.Field()
 
