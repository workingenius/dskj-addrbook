# -*- coding:utf8 -*-

from django.test import TestCase

from .models import (
    sort_staff_with_ch_pron, staffs_by_department,
    Staff, Contact, Department, Position)


# TODO: detail Exceptions


def gen_staff(name):
    s = Staff(**{'name': name})
    s.save()
    return s


def save(*objs):
    for obj in objs:
        obj.save()


class TestStaff(TestCase):
    def test_create_staff(self):
        Staff(**{
            'name': 'Alice',
        }).save()

        a = Staff.objects.get(name='Alice')
        assert a
        assert a.id

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


class TestContact(TestCase):
    def test_same_contact(self):
        s = gen_staff('Whatever')
        em = 'whatever@whatever.org'
        s.contact_set.create(mode=Contact.EMAIL, value=em)
        with self.assertRaises(Exception):
            s.contact_set.create(mode=Contact.EMAIL, value=em)


class TestDepartment(TestCase):
    def setUp(self):
        # d1 <- d2 <- d3
        d1 = Department(name='root', superior=None)
        d2 = Department(name='d1', superior=d1)
        d3 = Department(name='d2', superior=d2)
        self.ds = [d1, d2, d3]
        save(*self.ds)

        s1 = gen_staff('Alice')
        s2 = gen_staff('Bob')
        s3 = gen_staff('Cristle')
        s4 = gen_staff('David')
        s5 = gen_staff('Emma')
        s6 = gen_staff('Fever')
        self.ss = [s1, s2, s3, s4, s5, s6]

        p1 = Position(department=d1, staff=s1, job='manager')
        p2 = Position(department=d1, staff=s2, job='contacter')
        p3 = Position(department=d2, staff=s2, job='manager')
        p4 = Position(department=d2, staff=s3, job='sales')
        p5 = Position(department=d2, staff=s4)
        p6 = Position(department=d3, staff=s5, job='manager')
        p7 = Position(department=d3, staff=s6, job='maintainer')
        p8 = Position(department=d2, staff=s6, job='maintainer')
        self.ps = [p1, p2, p3, p4, p5, p6, p7, p8]
        save(*self.ps)

    def test_duplicate_department(self):
        d4 = Department(name='d1')
        with self.assertRaises(Exception):
            d4.save()

    def test_search_by_department(self):
        assert len(staffs_by_department(self.ds[0])) == 2
        assert len(staffs_by_department(self.ds[1])) == 4
        assert len(staffs_by_department(self.ds[2])) == 2

    def test_multi_job_in_same_department(self):
        p9 = Position(
            department=self.ds[2],
            staff=self.ss[4],
            job='speaker'
        )
        p9.save()
        assert len(Position.objects.all()) == 9
        assert len(staffs_by_department(self.ds[2])) == 2

    def test_position_should_be_unique(self):
        p10 = Position(
            department=self.ds[2],
            staff=self.ss[4],
            job='manager'
        )
        with self.assertRaises(Exception):
            p10.save()
