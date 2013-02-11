# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.pagination import (BasePaginationSerializer, NextPageField, PreviousPageField)
from companies.serializers import CompanySerializer
from .models import BluuSite


class SiteSerializer(serializers.ModelSerializer):
    contract_bluuuser = serializers.ManyPrimaryKeyRelatedField()
    company = CompanySerializer()

    class Meta:
        model = BluuSite
        fields = ('id', 'first_name', 'middle_initial', 'last_name', 'street',
            'city', 'state', 'zip_code', 'country', 'phone', 'email', 'company')


class SitePaginationSerializer(BasePaginationSerializer):
    sEcho = serializers.SerializerMethodField('get_echo')
    iTotalRecords = serializers.SerializerMethodField('get_itotal_records')
    iTotalDisplayRecords = serializers.Field(source='paginator.count')
    results_field = 'aaData'
    next = NextPageField(source='*')
    previous = PreviousPageField(source='*')

    def get_echo(self, obj):
        return self.context.get('request').QUERY_PARAMS.get('sEcho', None)

    def get_itotal_records(self, obj):
        return self.context['extra'].get('iTotalRecords', -1)

    def __init__(self, *args, **kwargs):
        super(SitePaginationSerializer, self).__init__(*args, **kwargs)
        

    class Meta:
        object_serializer_class = SiteSerializer
