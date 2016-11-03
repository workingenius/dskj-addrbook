# -*- coding:utf8 -*-

from collections import namedtuple

Contact = namedtuple('Contact', ['key', 'literal'])

email =     Contact(u'email',   u'邮件地址')
phone =     Contact(u'phone',   u'直线')
extnum = Contact(u'extnum', u'分机号')
fax =       Contact(u'fax',     u'传真')
mobile =    Contact(u'mobile',  u'手机')
qq =        Contact(u'qq',      u'QQ')
ip =       Contact(u'ip',     u'IP地址')

contacts = [
    extnum, phone, fax, mobile, qq, email
]
