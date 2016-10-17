# -*- coding:utf8 -*-
from decimal import Decimal
import re

import pandas as pd

from django.contrib.auth.models import User
from .models import Department, Staff, Position, Contact
from itertools import ifilter, imap
from .contacts import contacts


# ------------------------
# helpers

def reverted(dict):
    return {v: k for k, v in dict.iteritems()}


def read_excel(*args, **kwargs):

    def to_string(x):
        if pd.isnull(x):
            return None
        elif isinstance(x, (int, float, Decimal)):
            return str(int(x))
        else:
            return x

    df = pd.read_excel(*args, **kwargs)
    for column in df.columns:
        df[column] = df[column].map(to_string)
    return df


def with_columns(columns):
    def wrap_func(func):
        def wrapped_func(dataframe, *args, **kwargs):
            df = dataframe[columns]
            return func(df, *args, **kwargs)
        return wrapped_func
    return wrap_func


# users: {<literal>: <real name>}
users = {}

# departments: {<department name>: <superior name>}
departments = {}


@with_columns(u'使用人')
def _prepare_users(names, users):
    for name in names:
        if not name:
            continue
        real_name = process_locaff_name(name)
        users[name] = real_name


@with_columns([u'使用人', u'初始密码'])
def load_users(df):
    for i, row in df.iterrows():
        literal_name, password = tuple(row)
        if (not literal_name) or (not password):
            continue
        User.objects.create_user(literal_name, password=password)


def load_staffs(users):
    for literal_name, real_name in users.iteritems():
        try:
            user = User.objects.get(username=literal_name)
        except User.DoesNotExist:
            user = None
        Staff.objects.create(name=real_name, user=user)


def load_departments(df, departments, depart_column, superior_column=None):
    def new_depart(name, superior=None):
        if superior is not None:
            superior = process_department_name(superior)
        name = process_department_name(name)
        departments.setdefault(name, superior)

    if superior_column:
        df = df[[depart_column, superior_column]]
        df = df[~df[depart_column].isnull()]
        df = df.fillna(method='ffill')
        for i, row in df.iterrows():
            depart, superior = tuple(row)
            new_depart(depart, superior)
    else:
        ser = df[depart_column]
        ser = ser[~ser.isnull()]
        for depart in ser:
            new_depart(depart)


def save_departments(departments):
    def save_depart_aux(pending, done):
        depart_names = [name for name, supname in pending.items() if (supname in done) or (supname is None)]
        for name in depart_names:
            supname = pending[name]
            if supname is None:
                done[name] = Department.objects.create(name=name)
                del pending[name]
            else:
                done[name] = Department.objects.create(name=name, superior=done[supname])
                del pending[name]
        return pending, done

    for d, s in departments.iteritems():
        assert d != s

    departs = dict(departments)
    result = {}
    while len(departs):
        departs, result = save_depart_aux(departs, result)
    return result


locaff_ptn = re.compile(u'[(\uff08][\u517c\u5c0f][)\uff09]')
department_ptn = re.compile(r'\s')


def process_locaff_name(name):
    return locaff_ptn.sub(u'', name)


def process_department_name(name):
    return department_ptn.sub('', name)


def _from_xlsx_worksheet(dataframe):
    """format must be same as $BASE_DIR/assets/SLC.xlsx"""

    df = dataframe
    depart_columns = [u'地区', u'部门一', u'部门二']
    df[depart_columns] = df[depart_columns].fillna(method='ffill')
    rows = imap(lambda x: list(x[1].values), df.iterrows())

    contact_dict = {}
    for column_num, column_name in enumerate(df.columns):
        for c in contacts:
            if c.literal in column_name:
                contact_dict[column_num] = c

    REGIN = 0
    DEPART1 = 1
    DEPART2 = 2
    LOCAFF = 3

    def rv(row, idx):
        return row[idx]

    depart_name_set = set()
    last_d = [None]

    def handle_depart(depart_name, superior_depart=None):
        if depart_name is None:
            return
        depart_name = process_department_name(depart_name)
        if not depart_name in depart_name_set:
            depart_name_set.add(depart_name)
            d = Department(name=depart_name, superior=superior_depart)
            last_d[0] = d
            return d
        else:
            return Department.objects.get(name=depart_name)

    def handle_contact(contacts, row, idx, locaff):
        v = row[idx]
        if v:
            return Contact(staff=locaff, mode=contacts[idx].key, value=v)

    for row in rows:
        # row without locaff name is invalid
        locaff_name = rv(row, LOCAFF)
        if pd.isnull(locaff_name):
            continue

        regin = rv(row, REGIN)
        d1 = handle_depart(regin)
        yield d1

        depart1 = rv(row, DEPART1)
        d2 = handle_depart(depart1, d1)
        yield d2

        depart2 = rv(row, DEPART2)
        d3 = handle_depart(depart2, d2)
        yield d3

        # TODO: preprocess name, handle special cases
        locaff = Staff(
            name=process_locaff_name(locaff_name)
        )
        yield locaff

        pos = Position(department=(d3 or d2 or d1 or last_d[0]), staff=locaff)
        yield pos

        for column_num, contact in contact_dict.items():
            yield handle_contact(contact_dict, row, column_num, locaff)


def from_xlsx_worksheet(dataframe):
    return ifilter(None, _from_xlsx_worksheet(dataframe))


def load(path, sheetname):
    df = read_excel(path, sheetname)
    for obj in from_xlsx_worksheet(df):
        obj.save()


def load2(path, sheetname):
    df = read_excel(path, sheetname)
    _prepare_users(df, users)

    load_users(df)
    load_staffs(users)

    load_departments(df, departments, u'地区')
    load_departments(df, departments, u'部门一', u'地区')
    load_departments(df, departments, u'部门二', u'部门一')

    save_departments(departments)

