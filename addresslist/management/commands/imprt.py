# -*- coding:utf8 -*-
from django.core.management.base import BaseCommand
from addresslist.imprt import load


class Command(BaseCommand):
    help = 'import all enterprise database data from xlsx file'

    def add_arguments(self, parser):
        parser.add_argument('path')
        parser.add_argument('sheet')

    def handle(self, *args, **kwargs):
        sheetname = kwargs['sheet'].decode('utf8')
        load(kwargs['path'], sheetname)
        self.stdout.write('done')
