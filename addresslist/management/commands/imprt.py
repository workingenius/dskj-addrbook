# -*- coding:utf8 -*-

import openpyxl
from django.core.management.base import BaseCommand

from addresslist.imprt import from_xlsx_worksheet


class Command(BaseCommand):
    help = 'import all enterprise database data from xlsx file'

    def handle(self, *args, **kwargs):
        wb = openpyxl.load_workbook(filename='./assets/SLC.xlsx', read_only=True)
        ws = wb[u'配置']
        objs = from_xlsx_worksheet(ws)

        for obj in objs:
            obj.save()
