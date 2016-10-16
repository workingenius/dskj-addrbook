# -*- coding:utf8 -*-
from decimal import Decimal
import re

import pandas as pd

from .models import Department, Staff, Position, Contact
from itertools import ifilter, imap

locaff_ptn = re.compile(u'[(\uff08][\u517c\u5c0f][)\uff09]')
department_ptn = re.compile(r'\s')


def process_locaff_name(name):
    return locaff_ptn.sub(u'', name)


def process_department_name(name):
    return department_ptn.sub('', name)


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


def _from_xlsx_worksheet(dataframe):
    """format must be same as $BASE_DIR/assets/SLC.xlsx"""

    df = dataframe
    depart_columns = [u'地区', u'部门一', u'部门二']
    df[depart_columns] = df[depart_columns].fillna(method='ffill')
    rows = imap(lambda x: list(x[1].values), df.iterrows())

    REGIN = 0
    DEPART1 = 1
    DEPART2 = 2
    LOCAFF = 3
    OLD_EXTNUM = 4
    NEW_EXTNUM = 5
    PHONE = 6
    FAX = 7
    MOBILE = 8
    EMAIL = 9
    IM = 10
    PHONE_MAC = 11

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

    def handle_contact(row, idx, mode, locaff):
        v = rv(row, idx)
        if v:
            return Contact(staff=locaff, mode=mode, value=v)

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

        yield handle_contact(row, OLD_EXTNUM, 'OLD_EXTNUM', locaff)
        yield handle_contact(row, NEW_EXTNUM, 'NEW_EXTNUM', locaff)
        yield handle_contact(row, PHONE, 'PHONE', locaff)
        yield handle_contact(row, FAX, 'FAX', locaff)
        yield handle_contact(row, MOBILE, 'MOBILE', locaff)
        yield handle_contact(row, EMAIL, 'EMAIL', locaff)
        yield handle_contact(row, IM, 'EM', locaff)
        yield handle_contact(row, PHONE_MAC, 'PHONE_MAC', locaff)


def from_xlsx_worksheet(dataframe):
    return ifilter(None, _from_xlsx_worksheet(dataframe))
