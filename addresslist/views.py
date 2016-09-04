from django.shortcuts import render
from django.http import JsonResponse

from .models import (
    Staff, Position, Department, Contact
)
from .options import CONTACTS


def locaff(request, id):
    lcf = Staff.objects.get(id=id)

    depart = lcf.department_set.all()[0]

    contacts = lcf.contact_set.all()
    conts = []
    for c in contacts:
        conts.append({
            'mode': CONTACTS[c.mode],
            'value': c.value,
        })

    ctx = {
        'locaff': lcf.name,
        'department': depart.name,
        'contacts': conts,
    }

    return render(request, 'addresslist/_locaff.html', ctx)


def locaff_data(request, id):
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
