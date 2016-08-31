# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.db import models


class Staff(models.Model):
    name = models.CharField(max_length=32)
    gender = models.BooleanField()
    birthday = models.DateField(null=True)


class Contact(models.Model):
    staff = models.ForeignKey(Staff)
    mode = models.CharField(max_length=16) # communication mode, "phone", "qq", "email", etc.
    value = models.CharField(max_length=128)

    EMAIL = 'email'
    QQ = 'qq'
    PHONE = 'phone'


def create_staff(info, contacts=[]):
    staff = Staff(**info)
    staff.save()

    for c in contacts:
        contact = Contact(**c)
        contact.staff = staff
        contact.save()
