# -*- coding:utf8 -*-

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser

from .models import LocaffInfo
from .models import LocaffInfoSerializer


def main(request):
    return render(request, 'addresslist/main.html')


@csrf_exempt
def locaff_list(request):
    if request.method == 'GET':
        all_locaffs = LocaffInfo.get(lambda x: x.all())
        serializer = LocaffInfoSerializer(all_locaffs, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = LocaffInfoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


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
