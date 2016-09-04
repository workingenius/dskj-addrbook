from django.shortcuts import render

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

    return render(request, 'addresslist/locaff.html', ctx)

