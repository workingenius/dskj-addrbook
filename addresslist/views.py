from django.shortcuts import render
from django.http import JsonResponse

from .models import (
    Staff, Position, Department, Contact
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
    bd = map(lambda x: (x.id, x.name), lcfs)
    # TODO: WTF safe?
    return JsonResponse(bd, safe=False)
