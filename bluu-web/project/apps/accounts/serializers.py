# -*- coding: utf-8 -*-
from accounts import models
from django.contrib.auth.models import User
from rest_framework import serializers


class SiteSerializer(serializers.ModelSerializer):
    contract_bluuuser = serializers.ManyPrimaryKeyRelatedField()

    class Meta:
        model = models.Site
        fields = ('id', 'first_name', 'middle_initial', 'last_name', 'street',
            'city', 'state', 'zip_code', 'country', 'phone', 'email')


class BluuUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'snippets')


class CompanySerializer(serializers.ModelSerializer):
    company_bluuuser = serializers.ManyPrimaryKeyRelatedField()

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'contact_name', 'street',
            'city', 'state', 'zip_code', 'country', 'phone', 'email')


