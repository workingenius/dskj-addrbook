# -*- coding:utf8 -*-
from decimal import Decimal
import re

import pandas as pd

from .models import Department, Staff, Position, Contact
from itertools import ifilter, imap
from .contacts import contacts


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


locaff_ptn = re.compile(u'[(\uff08].*[)\uff09]')
department_ptn = re.compile(r'\s')


def process_locaff_name(name):
    return locaff_ptn.sub(u'', name)


def process_department_name(name):
    return department_ptn.sub('', name)


def _from_xlsx_worksheet(dataframe):
    """format must be same as $BASE_DIR/assets/SLC.xlsx"""

    df = dataframe
    depart_columns = [u'部门一', u'部门二']
    rows = imap(lambda x: list(x[1].values), df.iterrows())

    contact_dict = {}
    for column_num, column_name in enumerate(df.columns):
        for c in contacts:
            if c.literal in column_name:
                contact_dict[column_num] = c

    DEPART1 = 1
    DEPART2 = 2
    LOCAFF = 0

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

        ds = [last_d[0]]

        depart1 = rv(row, DEPART1)
        d1 = handle_depart(depart1)
        ds.append(d1)
        yield d1

        depart2 = rv(row, DEPART2)
        if depart2:
            d2 = handle_depart(depart2, d1)
            ds.append(d2)
            yield d2

        # TODO: preprocess name, handle special cases
        locaff = Staff(
            name=process_locaff_name(locaff_name)
        )
        yield locaff

        pos = Position(department=ds[-1], staff=locaff)
        yield pos

        for column_num, contact in contact_dict.items():
            yield handle_contact(contact_dict, row, column_num, locaff)


def from_xlsx_worksheet(dataframe):
    return ifilter(None, _from_xlsx_worksheet(dataframe))


def load(path, sheetname):
    df = read_excel(path, sheetname)
    for obj in from_xlsx_worksheet(df):
        obj.save()

