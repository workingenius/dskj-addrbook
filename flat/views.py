# -*- coding: utf8 -*-
import urllib
from StringIO import StringIO

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.viewsets import ModelViewSet

from flat.xlsx import output
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


@csrf_exempt
def export(request):
    # TODO: invalid parameters
    id_list = request.POST.get('id_list')
    id_list = map(int, id_list.split(','))
    work_book = output(id_list)

    f = StringIO()
    work_book.save(f)

    rsp = HttpResponse(f.getvalue())
    rsp['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    filename = u'资生堂通讯录(%s人).xlsx' % len(id_list)
    bf = request.user_agent.browser.family.lower()
    if 'ie' in bf:
        rsp['Content-Disposition'] = 'attachment; filename="%s"' % (
                urllib.quote(filename.encode('utf8')))
    else:
        rsp['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % (
                urllib.quote(filename.encode('utf8')))

    return rsp
