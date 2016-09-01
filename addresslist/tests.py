# -*- coding:utf8 -*-

from django.test import TestCase

from .models import (
    create_staff, sort_staff_with_ch_pron,
    Staff, Contact, Department, Position)


def gen_staff(name):
    return create_staff({'name': name, 'gender': True})


def save(*objs):
    for obj in objs:
        obj.save()


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


class TestDepartment(TestCase):
    def test_search_by_department(self):
        # d1 <- d2 <- d3
        d1 = Department(name='root', superior=None)
        d2 = Department(name='d1', superior=d1)
        d3 = Department(name='d2', superior=d2)

        save(d1, d2, d3)

        s1 = gen_staff('Alice')
        s2 = gen_staff('Bob')
        s3 = gen_staff('Cristle')
        s4 = gen_staff('David')
        s5 = gen_staff('Emma')
        s6 = gen_staff('Fever')

        m1 = Position(department=d1, staff=s1, job='manager')
        m2 = Position(department=d1, staff=s2, job='contacter')
        m3 = Position(department=d2, staff=s2, job='manager')
        m4 = Position(department=d2, staff=s3, job='sales')
        m5 = Position(department=d2, staff=s4)
        m6 = Position(department=d3, staff=s5, job='manager')
        m7 = Position(department=d3, staff=s6, job='maintainer')
        m8 = Position(department=d2, staff=s6, job='maintainer')
        save(m1, m2, m3, m4, m5, m6, m7, m8)


        assert len(d1.staffs.all()) == 2
        assert len(d2.staffs.all()) == 4
        assert len(d3.staffs.all()) == 2