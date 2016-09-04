from django.shortcuts import render

from .models import (
    Staff, Position, Department, Contact
)

def locaff(request, id):
    locaff = Staff.objects.get(id=id)
    contacts = locaff.contact_set.all()

    ctx = {
        'locaff': locaff.name,
        'contacts': contacts,
    }

    return render(request, 'addresslist/locaff.html', ctx)

