from django.shortcuts import render

from .models import (
    Staff, Position, Department, Contact
)
from .options import CONTACTS

def locaff(request, id):
    locaff = Staff.objects.get(id=id)
    contacts = locaff.contact_set.all()

    conts = []
    for c in contacts:
        conts.append({
            'mode': CONTACTS[c.mode],
            'value': c.value,
        })

    ctx = {
        'locaff': locaff.name,
        'contacts': conts,
    }

    return render(request, 'addresslist/locaff.html', ctx)

