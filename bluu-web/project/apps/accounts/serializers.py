# -*- coding: utf-8 -*-
from accounts import models
from rest_framework import serializers


class BluuUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BluuUser
        fields = ('url', 'username', 'snippets')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BluuUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class Invitation(object):
    def __init__(self, email, groups):
        self.email = email
        self.groups = groups


class InvitationSerializer(serializers.Serializer):
    email = serializers.CharField()
    groups = serializers.RelatedField()

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.title = attrs['email']
            instance.groups = attrs['groups']
            return instance
        return Invitation(**attrs)
