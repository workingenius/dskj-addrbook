# -*- coding:utf8 -*-

from StringIO import StringIO
import json
import urllib

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView

from .models import LocaffInfo, Staff
from .models import LocaffInfoSerializer, UserSerializer
from .models import department_tree
from .xlsx import output


def _department_tree():
    dt = department_tree()

    def consdt(dt, level):
        head = dt[0]
        leaves = dt[1:]
        node = {
            'department' + str(level) : head.name,
        }
        infs = [consdt(d, level+1) for d in leaves]
        if infs:
            node['department' + str(level + 1)] = infs
        return node

    return [consdt(d, 1) for d in dt[1:]]


def main(request):
    if isinstance(request.user, AnonymousUser):
        ctx = {'user': 'null'}
    else:
        u = UserSerializer(request.user).data
        ctx = {'user': json.dumps(u), 'username': u['username']}
    ctx['department_tree'] = json.dumps(_department_tree())
    return render(request, 'addresslist/main.html', ctx)


class LocaffList(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None):
        all_locaffs = LocaffInfo.get(lambda x: x.all())
        serializer = LocaffInfoSerializer(all_locaffs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = LocaffInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocaffDetail(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def get_object(self, id):
        try:
            return LocaffInfo.get(lambda x: x.get(id=int(id)))
        except Staff.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        locaff = self.get_object(id)
        serializer = LocaffInfoSerializer(locaff)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        locaff = self.get_object(id)
        serializer = LocaffInfoSerializer(locaff, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        locaff = self.get_object(id)
        locaff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def export(request):
    # TODO: invalid parameters
    id_list = request.GET.get('id_list')
    id_list = map(int, id_list.split(','))
    work_book = output(id_list)

    f = StringIO()
    work_book.save(f)

    rsp = HttpResponse(f.getvalue())
    rsp['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    filename = u'资生堂通讯录(%s人).xlsx' % len(id_list)
    bf = request.user_agent.browser.family.lower()
    if ('ie' in bf):
        rsp['Content-Disposition'] = 'attachment; filename="%s"' % ( 
                urllib.quote(filename.encode('utf8')))
    else:
        rsp['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'%s' % (
                urllib.quote(filename.encode('utf8')))

    return rsp

