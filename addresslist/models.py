# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.db import models

from . import langs


class Staff(models.Model):
    name = models.CharField(max_length=32)
    gender = models.BooleanField()
    birthday = models.DateField(null=True)
    jp_pron = models.CharField(max_length=64, null=True) # japanese pronunciation
    ch_pron = models.CharField(max_length=64, null=True) # chinese pronunciation


class Contact(models.Model):
    staff = models.ForeignKey(Staff)
    mode = models.CharField(max_length=16) # communication mode, "phone", "qq", "email", etc.
    value = models.CharField(max_length=128)

    EMAIL = 'email'
    QQ = 'qq'
    PHONE = 'phone'


def create_staff(info, contacts=[]):
    staff = Staff(**info)
    staff.name = unicode(staff.name)

    if staff.ch_pron is None:
        staff.ch_pron = langs.ch_pinyin(staff.name)
    staff.save()

    for c in contacts:
        contact = Contact(**c)
        contact.staff = staff
        contact.save()

    return staff


def sort_staff_with_ch_pron(staff_list):
    return sorted(staff_list, key=lambda x: (x.ch_pron, x.name))