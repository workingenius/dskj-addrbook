# -*- coding:utf8 -*-

from collections import defaultdict

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse

from .models import (
    Staff, Position, Department, Contact,
    LocaffInfo,
    sort_staff_with_ch_pron,
    search as search_staff
)
from .options import CONTACTS


def main(request):
    return render(request, 'addresslist/main.html')


def locaff(request, id):
    try:
        lcf = Staff.objects.get(id=id)
    except Staff.DoesNotExist:
        return JsonResponse({}, status=404
                            )
    contacts = lcf.contacts.all()

    departs = list(lcf.departments.all())
    if len(departs):
        depart = departs[0].name
    else:
        depart = None

    lcfd = {
        'name': lcf.name,
        'department': depart,
        'contacts': [(CONTACTS[c.mode], c.value) for c in contacts]
    }

    return JsonResponse(lcfd)


def locaffs(request):
    lcfs = Staff.objects.all()
    lcfs = sort_staff_with_ch_pron(lcfs)

    clsfy = request.GET.get('classify')
    if not clsfy:
        bd = map(lambda x: (x.id, x.name), lcfs)
        # TODO: WTF safe?
        return JsonResponse(bd, safe=False)
    elif clsfy == 'capital':
        capital_dict = defaultdict(list)
        for lcf in lcfs:
            capital_dict[lcf.ch_pron[0]].append((lcf.id, lcf.name))
        capital_list = sorted(capital_dict.items())
        return JsonResponse(capital_list, safe=False)


def search(request):
    q = request.GET.get('query')
    locaffs = search_staff(q)
    locaffs = sort_staff_with_ch_pron(locaffs)
    names = map(lambda lcf: (lcf.id, lcf.name), locaffs)
    return JsonResponse(names, safe=False)


def all_locaffs(request):
    all_locaffs = LocaffInfo.get(lambda x: x.all())
    all_lcfs = []
    for lcf in all_locaffs:
        js = lcf.to_json()
        js['staff_id'] = js['id']
        del js['id']
        all_lcfs.append(js)
    return JsonResponse(all_lcfs, safe=False)


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
