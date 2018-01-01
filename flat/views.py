from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet

from .models import Record
from .serializers import RecordSerializer


class RecordViewSet(ModelViewSet):
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    lookup_field = 'id'


record_list = RecordViewSet.as_view({
    'get': 'list',
    'post': 'create',
})


record_detail = RecordViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})
