# -*- coding:utf8 -*-

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView

from .models import LocaffInfo, Staff
from .models import LocaffInfoSerializer


def main(request):
    return render(request, 'addresslist/main.html')


class LocaffList(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LocaffList, self).dispatch(request, *args, **kwargs)

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
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LocaffDetail, self).dispatch(request, *args, **kwargs)

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
    from .xlsx import output

    # TODO: invalid parameters
    id_list = request.GET.get('id_list')
    id_list = map(int, id_list.split(','))
    work_book = output(id_list)

    filename = '资生堂通讯录(%s人).xlsx' % len(id_list)

    rsp = HttpResponse()
    rsp['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    rsp['Content-Disposition'] = 'attachment; filename="%s"' % filename
    work_book.save(rsp)

    return rsp

