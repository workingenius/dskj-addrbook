# -*- coding:utf8 -*-

from collections import defaultdict

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse

from .models import (
    Staff, Position, Department, Contact,
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
    contacts = lcf.contact_set.all()

    departs = list(lcf.department_set.all())
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
    all_locaffs = (Staff.objects
                   .prefetch_related('contacts')
                   .prefetch_related('departments__superior')
                   .all())

    all_lcfs = []
    for locaff in all_locaffs:
        o = {}
        o['name'] = locaff.name
        for contact in locaff.contacts.all():
            o[contact.mode.lower()] = contact.value
        depart = locaff.departments.all()[0]
        o['depart1'] = depart.superior.name
        o['depart2'] = depart.name
        if o['depart1'] == u'北京亦庄工厂':
            o['depart1'] = o['depart2']
        all_lcfs.append(o)
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
