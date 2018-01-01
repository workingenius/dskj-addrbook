# -*- coding:utf8 -*-

import openpyxl
from .models import Record


def output(id_list):
    wb = openpyxl.Workbook()
    ws1 = wb.active

    fields = ('name', 'depart1', 'depart2', 'extnum',
              'phone', 'fax', 'mobile', 'qq', 'email')

    captions = (u'姓名', u'部门1', u'部门2', u'分机号',
                u'直线', u'传真', u'手机', u'qq', u'email')
    ws1.append(list(captions))

    for rec in Record.objects.filter(id__in=id_list):
        row = [getattr(rec, f, None) for f in fields]
        ws1.append(row)

    return wb
