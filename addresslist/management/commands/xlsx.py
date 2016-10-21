# -*- coding:utf8 -*-

from django.core.management.base import BaseCommand
from addresslist.xlsx import output


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('id_list')

    def handle(self, *args, **kwargs):
        id_list = kwargs['id_list']
        id_list = map(int, id_list.split(','))

        wb = output(id_list)
        wb.save('output.xlsx')
