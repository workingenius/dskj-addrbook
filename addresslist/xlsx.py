# -*- coding:utf8 -*-

import openpyxl
from .models import Staff

def output(id_list):
    staffs = Staff.objects.filter(id__in=id_list)
    staffs = (staffs
              .prefetch_related('contacts')
              .prefetch_related('departments'))
    staffs = staffs.all()

    wb = openpyxl.Workbook()
    ws1 = wb.active

    ws1.append([
        u'姓名',
        u'部门1',
        u'部门2',
        u'号码',
        u'邮件',
        u'QQ',
    ])

    for staff in staffs:

        # departs
        depart = staff.departments.all()[0]
        depart1 = depart.superior.name
        depart2 = depart.name
        if depart1 == u'北京亦庄工厂':
            depart1 = depart2

        # concats
        contacts = staff.contacts.all()
        cts = {}
        for c in contacts:
            cts[c.mode] = c.value

        row = [
            staff.name,
            depart1,
            depart2,
            cts.get('PHONE'),
            cts.get('EMAIL'),
            cts.get('QQ'),
        ]

        ws1.append(row)

    return wb
