# -*- coding:utf8 -*-

from django.test import TestCase

from .models import (create_staff,
                     Staff)


class TestStaff(TestCase):
    def test_create_staff(self):
        create_staff({
            'name': 'Alice',
            'gender': True,
        })

        a = Staff.objects.get(name='Alice')
        assert a
        assert a.id