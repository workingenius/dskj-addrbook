# -*- coding:utf8 -*-
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from .models import Record


class RecordSerializer(ModelSerializer):
    class Meta:
        model = Record
        fields = ('id', 'name', 'depart1', 'depart2', 'extnum',
                  'phone', 'fax', 'mobile', 'qq', 'email', 'staff_num')


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )
