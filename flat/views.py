# -*- coding: utf8 -*-
import json
import urllib
from StringIO import StringIO

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework.viewsets import ModelViewSet

from flat.xlsx import output
from .models import Record, Department
from .serializers import RecordSerializer, UserSerializer


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


def main(request):
    def _department_tree():
        dt = Department.department_tree()

        def consdt(dt, level):
            head = dt[0]
            leaves = dt[1:]
            node = {
                'department' + str(level): head.name,
            }
            infs = [consdt(d, level + 1) for d in leaves]
            if infs:
                node['department' + str(level + 1)] = infs
            return node

        return [consdt(d, 1) for d in dt[1:]]

    if isinstance(request.user, AnonymousUser):
        ctx = {'user': 'null'}
    else:
        u = UserSerializer(request.user).data
        ctx = {'user': json.dumps(u), 'username': u['username']}
    ctx['department_tree'] = json.dumps(_department_tree())
    return render(request, 'flat/main.html', ctx)
