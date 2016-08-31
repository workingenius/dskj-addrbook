# -*- coding:utf8 -*-

from django.test import TestCase

from .models import (create_staff,
                     Staff, Contact)


class TestStaff(TestCase):
    def test_create_staff(self):
        create_staff({
            'name': 'Alice',
            'gender': True,
        })

        a = Staff.objects.get(name='Alice')
        assert a
        assert a.id

    def test_create_staff_with_contacts(self):
        bob = {'name': 'Bob', 'gender': False}
        bobsemail = 'bob@test.com'
        phone = {'mode': Contact.EMAIL, 'value': bobsemail}

        create_staff(bob, [phone])

        b = Staff.objects.get(name='Bob')
        assert b
        assert b.id

        c = Contact.objects.get(mode=Contact.EMAIL, value=bobsemail)
        assert c
        assert c.id