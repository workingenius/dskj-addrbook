# -*- coding:utf8 -*-

import openpyxl
from .models import LocaffInfo
from .contacts import contacts


def output(id_list):
    wb = openpyxl.Workbook()
    ws1 = wb.active

    fields = (['name', 'depart1', 'depart2']
              + [c.key for c in contacts])

    head = [
        u'姓名',
        u'部门1',
        u'部门2',
    ] + map(lambda c: c.literal, contacts)
    ws1.append(head)

    staffs = LocaffInfo.get(lambda x: x.filter(id__in=id_list))
    for staff in staffs:
        row = [staff.__dict__.get(f, None) for f in fields]
        ws1.append(row)

    return wb
