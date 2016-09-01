# -*- coding:utf8 -*-

import openpyxl
from django.core.management.base import BaseCommand
from django.core.management import call_command

from addresslist.imprt import from_xlsx_worksheet


class Command(BaseCommand):
    help = 'import all enterprise database data from xlsx file'

    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('sheet')

    def handle(self, *args, **kwargs):
        call_command('flush', interactive=False)

        wb = openpyxl.load_workbook(filename=kwargs['path'], read_only=True)
        sheet = kwargs['sheet'].decode('utf8')
        ws = wb[sheet]
        objs = from_xlsx_worksheet(ws)

        for obj in objs:
            obj.save()

        self.stdout.write('done')