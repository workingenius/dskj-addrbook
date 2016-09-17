from collections import defaultdict

from django.shortcuts import render
from django.http import JsonResponse

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
