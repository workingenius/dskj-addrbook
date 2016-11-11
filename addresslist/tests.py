# -*- coding:utf8 -*-
import json
import re
from itertools import imap
from functools import partial

from django.test import TestCase
import pandas as pd

from .models import (
    sort_staff_with_ch_pron, staffs_by_department,
    search,
    Staff, Contact, Department, Position,
    LocaffInfo)
from models import LocaffInfoSerializer
from .langs import ch_pinyin
from .imprt import (
    from_xlsx_worksheet, read_excel)

from django.contrib.auth.models import User


# TODO: detail Exceptions


def gen_staff(name, id=None):
    meta = {'name': name}
    if id:
        meta['id'] = id
    s = Staff(**meta)
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
        assert s2.ch_pron == 'ZHITIANXINZHANG' # usually read 'ZHITIANXINCHANG', while that's ok
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


SOURCE_PATH = './assets/SLC2.xlsx'
SOURCE_SHEETNAME = u'配置'
test_df = read_excel(SOURCE_PATH, sheetname=SOURCE_SHEETNAME)


class EnvForImportData(TestCase):
    def setUp(self):
        self.df = test_df
        objs = from_xlsx_worksheet(self.df)

        for obj in objs:
            obj.save()


class TestImportData(EnvForImportData):
    def test_data_type(self):
        # currently, no number
        rows = self.df.iterrows()
        for i, row in rows:
            for value in list(row):
                assert (
                    isinstance(value, basestring)
                    or pd.isnull(value)
                )

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
        d3 = Department.objects.get(name=u'财务部')
        d4 = Department.objects.get(name=u'经营管理本部')
        assert d3.superior == d4


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


class TestLocaffInfo(TestCase):
    def test_create(self):
        with self.assertRaises(Exception):
            # no such department yet
            s = LocaffInfo(name='newstaff', depart1='d1', depart2='d2', email='s1@comp.com')
            s.save()

        Department.objects.create(name='d2')
        s = LocaffInfo(name='newstaff', depart1='d1', depart2='d2', email='s1@comp.com')
        s.save()
        assert s.id

    def test_multi_get(self):
        Department.objects.create(name='d2')
        s = LocaffInfo(name='newstaff', depart1='d1', depart2='d2', email='s1@comp.com')
        s.save()

        lis = LocaffInfo.get(lambda x: x.all())
        li = list(lis)[0]

        assert li.id is not None
        assert li.name
        assert li.email
        assert li.depart1

    def test_single_get(self):
        Department.objects.create(name='d2')
        s = LocaffInfo(name='newstaff', depart1='d1', depart2='d2', email='s1@comp.com')
        s.save()

        li = LocaffInfo.get(lambda x: x.get(name='newstaff'))
        assert li.id is not None
        assert li.name
        assert li.email
        assert li.depart1


    def test_delete(self):
        Department.objects.create(name='d2')
        s = LocaffInfo(name='newstaff', depart1='d1', depart2='d2', email='s1@comp.com')

        assert s.delete() is None

        s.save()

        d = s.delete()
        assert d
        assert list(Contact.objects.all()) == []

    def test_update(self):
        Department.objects.create(name='d2')
        Department.objects.create(name='d3')
        s = LocaffInfo(name='newstaff', depart1='d1', depart2='d2',
                       email='s1@comp.com', phone='123')
        s.save()

        s.name = 'modified'
        s.depart2 = 'd3'
        s.email = 'modified@comp.com'
        s.qq = 'anewqq'
        del s.phone
        s.save()

        s = LocaffInfo.get(lambda x: x.get(id=s.id))

        assert s.name == 'modified'
        assert s.depart1 == 'd3'
        assert s.email == 'modified@comp.com'
        assert s.qq == 'anewqq'
        assert hasattr(s, 'phone') == False


TEST_USER_NAME = 'testuser'
TEST_USER_PASSWORD = 'test*User'


def req(method, client, url, body=None, headers=None):
    if body:
        return getattr(client, method)(url, json.dumps(body), content_type='application/json')
    else:
        return getattr(client, method)(url)


def login(client):
    return client.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)


post = partial(req, 'post')
put = partial(req, 'put')
delete = partial(req, 'delete')


class TestCurrentApis(TestCase):
    def setUp(self):
        # test user for auth
        User.objects.create_user(TEST_USER_NAME, password=TEST_USER_PASSWORD)

        # d1 <- d2 <- d3
        d1 = Department(name='市场部', superior=None)
        d2 = Department(name='技术部', superior=d1)
        d3 = Department(name='人事部', superior=d2)
        self.ds = [d1, d2, d3]
        save(*self.ds)

        s1 = gen_staff('Alice', id=1)
        s2 = gen_staff('Bob', id=2)
        s3 = gen_staff('Cristle', id=3)
        s4 = gen_staff('David', id=4)
        s5 = gen_staff('Emma', id=5)
        s6 = gen_staff('Fever', id=6)
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

        c1 = Contact(staff=s2, mode='email', value='bob@comp.com')
        c1.save()

    def test_get_locaff_list(self):
        alcfs = self.client.get('/staffs').json()
        assert len(alcfs)
        for lcf in alcfs:
            assert lcf['id'] is not None
            assert lcf['name']
            assert lcf['depart1']
            assert lcf.has_key('depart2')

    def test_create_locaff(self):
        body = {
            'name': 'newstaff1',
            'depart1': '技术部',
            'email': 'newstaff1@comp.com'
        }
        assert post(self.client, '/staffs', body).status_code == 403
        login(self.client)
        assert post(self.client, '/staffs', body).json()['id'] is not None

    def test_get_locaff_detail(self):
        resp = self.client.get('/staffs/2')
        assert resp.status_code == 200
        staff = resp.json()
        assert staff['id'] == 2
        assert staff['name'] == 'Bob'
        assert staff['depart1'] == u'市场部'
        assert staff['depart2'] is None
        assert staff['email'] == 'bob@comp.com'

    def test_update_locaff_detail(self):
        phonenum = '2910394'
        body = {
            'name': 'Alice',
            'depart1': u'技术部',
            'email': 'alice@comp.com',
            'phone': phonenum,
        }

        assert put(self.client, '/staffs/1', body).status_code == 403
        login(self.client)
        resp = put(self.client, '/staffs/1', body)
        assert 200 <= resp.status_code < 300
        resp = resp.json()
        assert resp['id'] == 1

        # TODO: pass them
        # assert resp['depart1'] == u'市场部'
        # assert resp['depart2'] == u'技术部'

        assert resp['name'] == 'Alice'
        assert resp['email'] == 'alice@comp.com'
        assert resp['phone'] == phonenum

        resp = self.client.get('/staffs/1').json()
        assert resp['id'] == 1
        assert resp['name'] == 'Alice'
        assert resp['email'] == 'alice@comp.com'
        assert resp['phone'] == phonenum

    def test_delete_locaff_info(self):
        assert delete(self.client, '/staffs/1').status_code == 403
        login(self.client)
        resp = delete(self.client, '/staffs/1')
        assert 200 <= resp.status_code < 300
        resp = delete(self.client, '/staffs/1')
        assert resp.status_code == 404


class TestSerializer(TestCase):
    def setUp(self):
        d1 = Department.objects.create(name='d1')
        Department.objects.create(name='d2')
        Department.objects.create(name='d3', superior=d1)
        s = LocaffInfo(name='newstaff', depart1='d1', depart2='d2',
                       email='s1@comp.com', phone='123')
        s.name = 'modified'
        s.depart2 = 'd3'
        s.email = 'modified@comp.com'
        s.qq = 'anewqq'
        del s.phone
        s.save()
        self.locaff_info = s

    def test_serialize(self):
        s = self.locaff_info
        jsondata = LocaffInfoSerializer(s).data
        assert jsondata['name'] == 'modified'
        assert jsondata['depart1'] == 'd1'
        assert jsondata['depart2'] == 'd3'
        assert jsondata['email'] == 'modified@comp.com'
        assert jsondata['qq'] == 'anewqq'
        assert jsondata.get('phone') is None

    def test_deserialize(self):
        jsondata = {"name":"name", "depart1":"d3"}
        s = LocaffInfoSerializer(data=jsondata)
        s.is_valid()
        s.save()

        s = LocaffInfo.get(lambda x: x.get(name="name"))
        assert s.depart2 == 'd3'
        assert s.depart1 == 'd1'

