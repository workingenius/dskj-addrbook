# -*- coding:utf8 -*-

import pandas as pd
from flat.models import Record


def fmt(x):
    if pd.isnull(x):
        return None
    else:
        return x


df = pd.read_excel('assets/SLC3.xlsx', u'最新通讯录')
for idx, row in df.iterrows():
    r = Record(
        name=fmt(row[u'姓名']),
        depart1=fmt(row[u'部门1']),
        depart2=fmt(row[u'部门2']),
        extnum=fmt(row[u'分机号']),
        phone=fmt(row[u'直线']),
        fax=fmt(row[u'传真']),
        mobile=fmt(row[u'手机']),
        qq=fmt(row[u'QQ']),
        email=fmt(row[u'邮件地址'])
    )
    r.save()
