# -*- coding:utf8 -*-

import re
import json
from itertools import imap

from django.test import TestCase, Client
from django.test.utils import skipIf
import openpyxl

from .models import (
    sort_staff_with_ch_pron, staffs_by_department,
    search,
    Staff, Contact, Department, Position)
from .langs import ch_pinyin
from .imprt import from_xlsx_worksheet
from . import options


# TODO: detail Exceptions


def gen_staff(name):
    s = Staff(**{'name': name})
    s.save()
    return s


def save(*objs):
    for obj in objs:
        obj.save()


class TestLangs(TestCase):
    def test_ch_pinyin_start_with_number(self):
        assert ch_pinyin(u'1车间') == '~CHEJIAN'
        assert ch_pinyin(u'2车间') == '~CHEJIAN'
        assert ch_pinyin(u'_车间') == '~CHEJIAN'


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
        s.contacts.create(mode=Contact.EMAIL, value=em)
        with self.assertRaises(Exception):
            s.contacts.create(mode=Contact.EMAIL, value=em)


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


class TestImportData(TestCase):
    def setUp(self):
        wb = openpyxl.load_workbook(filename='./assets/SLC.xlsx', read_only=True)
        ws = wb[u'配置']
        objs = from_xlsx_worksheet(ws)

        for obj in objs:
            obj.save()

    def test_import_from_xlsx(self):
        # setUp should pass
        pass

    def test_contact_values_should_be_string(self):
        contacts = Contact.objects.all()
        values = imap(lambda r: r.value, contacts)
        assert all(map(lambda v: isinstance(v, basestring), values))

    def test_preprocess_locaff_name(self):
        locaffs = Staff.objects.all()
        names = imap(lambda r: r.name, locaffs)

        ptn = re.compile(u'[(\uff08][\u517c\u5c0f][)\uff09]')

        def valid(name):
            if ptn.search(name):
                print name
                return False
            return True

        assert all(imap(valid, names))

    def test_departments_should_not_contain_blanks(self):
        departments = Department.objects.all()
        names = imap(lambda r: r.name, departments)

        ptn = re.compile(r'\s')

        def valid(name):
            if ptn.search(name):
                print name
                return False
            return True

        assert all(imap(valid, names))

    def test_superiors(self):
        d1 = Department.objects.get(name=u'经营监察部')
        d2 = Department.objects.get(name=u'北京亦庄工厂')
        assert d1.superior == d2

        d3 = Department.objects.get(name=u'财务部')
        d4 = Department.objects.get(name=u'经营管理本部')
        assert d3.superior == d4


@skipIf(True, 'considering deprecating')
class TestApi(TestCase):
    def setUp(self):
        s1 = Staff.objects.create(name='Alice')
        c11 = Contact(mode='EMAIL', value='alice@gmail.com')
        s1.contacts.add(c11, bulk=False)

        s2 = Staff.objects.create(name='Bob')

        s3 = Staff.objects.create(name='Cherry')
        d3 = Department.objects.create(name='CherrySDepartment')
        p3 = Position.objects.create(staff=s3, department=d3)

    def test_locaff(self):
        c = Client()
        response = c.get('/locaff/1')
        assert 200 <= response.status_code < 300
        d = json.loads(response.content)
        assert d['name'] == 'Alice'
        assert d['department'] is None
        assert len(d['contacts']) == 1

        response = c.get('/locaff/2')
        assert 200 <= response.status_code < 300
        d = json.loads(response.content)
        assert d['name'] == 'Bob'
        assert d['department'] is None
        assert len(d['contacts']) == 0

        response = c.get('/locaff/3')
        assert 200 <= response.status_code < 300
        d = json.loads(response.content)
        assert d['name'] == 'Cherry'
        assert d['department'] == 'CherrySDepartment'
        assert len(d['contacts']) == 0

    def test_404(self):
        c = Client()
        response = c.get('/locaff/10')
        assert response.status_code == 404

    def test_readable_contacts(self):
        c = Client()
        response = c.get('/locaff/1')
        assert 200 <= response.status_code < 300
        d = json.loads(response.content)
        assert len(d['contacts']) == 1

        readable_contacts = options.CONTACTS.values()
        for c in d['contacts']:
            assert c[0] in readable_contacts

    def test_list_locaff(self):
        c = Client()
        response = c.get('/locaff/')
        assert 200 <= response.status_code < 300
        d = json.loads(response.content)
        assert len(d) == 3

    def test_list_locaff_classify(self):
        c = Client()
        response = c.get('/locaff/?classify=capital')
        assert 200 <= response.status_code < 300
        d = json.loads(response.content)
        assert len(d) == 3
        assert isinstance(d, list)
        assert map(lambda x: x[0], d) == [u'A', u'B', u'C']  # should be sorted

    def test_search(self):
        rsp = self.client.get('/search?query=Cherry').json()
        self.assertIsInstance(rsp, list)
        assert len(rsp)
        for i in rsp:
            self.assertIsInstance(i, list)


@skipIf(True, 'considering deprecating')
class TestSearch(TestCase):
    def setUp(self):
        # d1 <- d2 <- d3
        d1 = Department(name='市场部', superior=None)
        d2 = Department(name='技术部', superior=d1)
        d3 = Department(name='人事部', superior=d2)
        self.ds = [d1, d2, d3]
        save(*self.ds)

        s1 = gen_staff('Alice')
        s2 = gen_staff('Bob')
        s3 = gen_staff('Cristle')
        s4 = gen_staff('David')
        s5 = gen_staff('Emma')
        s6 = gen_staff('Fever')
        self.ss = [s1, s2, s3, s4, s5, s6]
        save(*self.ss)

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

    def test_search_by_department(self):
        self.assertEqual(len(search('市场')), 2)
        self.assertEqual(len(search('技术')), 4)
        self.assertEqual(len(search('人事')), 2)
