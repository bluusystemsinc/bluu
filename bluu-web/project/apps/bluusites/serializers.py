# -*- coding: utf-8 -*-
from rest_framework import serializers
from companies.serializers import CompanySerializer
from .models import BluuSite


class SiteSerializer(serializers.ModelSerializer):
    contract_bluuuser = serializers.ManyPrimaryKeyRelatedField()
    company = CompanySerializer()

    class Meta:
        model = BluuSite
        fields = ('id', 'first_name', 'middle_initial', 'last_name', 'street',
            'city', 'state', 'zip_code', 'country', 'phone', 'email', 'company')



