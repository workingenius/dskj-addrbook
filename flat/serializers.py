# -*- coding:utf8 -*-

from rest_framework.serializers import ModelSerializer
from .models import Record


class RecordSerializer(ModelSerializer):
    class Meta:
        model = Record
        fields = ('id', 'name', 'depart1', 'depart2', 'extnum',
                  'phone', 'fax', 'mobile', 'qq', 'email')
