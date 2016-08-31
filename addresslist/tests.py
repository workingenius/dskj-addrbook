# -*- coding:utf8 -*-

from django.test import TestCase

from .models import (
    create_staff, sort_staff_with_ch_pron,
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

    def test_staff_with_ch_pron(self):
        def gen_staff(name):
            return create_staff({'name': name, 'gender': True})

        s1 = gen_staff(u'曹操')
        s2 = gen_staff(u'織田信長')
        s3 = gen_staff(u'George Washington')
        s4 = gen_staff(u'安倍晴明')
        s5 = gen_staff(u'働畑鰯')  # test characters that do not exist in Chinese
        s6 = gen_staff(u'おだのぶなが')  # test hiragana
        s7 = gen_staff(u'タコヤキ')  # test katakana

        assert s1.ch_pron == 'CAOCAO'
        # assert s2.ch_pron == 'zhitianxinchang' # 'zhitianxinzhang' in fact, that's ok
        assert s3.ch_pron == 'GEORGEWASHINGTON'
        assert s4.ch_pron == 'ANBEIQINGMING'
        # s5 is meaningless

        ss = sort_staff_with_ch_pron([
            s1, s2, s3, s4, s5, s6, s7
        ])
        assert ss[:-2] == [s4, s1, s5, s3, s2]