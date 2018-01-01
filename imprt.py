# -*- coding:utf8 -*-

import pandas as pd
from flat.models import Record


df = pd.read_excel('assets/SLC3.xlsx', u'最新通讯录')
for idx, row in df.iterrows():
    r = Record(
        name=row[u'姓名'],
        depart1=row[u'部门1'],
        depart2=row[u'部门2'],
        extnum=row[u'分机号'],
        phone=row[u'直线'],
        fax=row[u'传真'],
        mobile=row[u'手机'],
        qq=row[u'QQ'],
        email=row[u'邮件地址']
    )
    r.save()
