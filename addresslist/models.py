# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_init

from . import langs


class Staff(models.Model):
    """
    a class whose instances stands for objects that has contacts, including staff and location.
    Best name may be "Locaff", which combines the two. We choose to skip staff -> locaff rename
    but this concept should be kept in mind.

    check $BASE_DIR/assets/SLC.xlsx for its data logic

    As the system grow, this structure is going to be more and more awkward. While for a
    company less than 1000 people, migration can be done by database rebuild. So difficulties
    in db migration does not count at all.
    """
    name = models.CharField(max_length=32)
    birthday = models.DateField(null=True)
    jp_pron = models.CharField(max_length=64, null=True)  # japanese pronunciation
    # TODO: implement Chinese pronunciation
    ch_pron = models.CharField(max_length=64, null=True)  # chinese pronunciation


def init_staff(**kwargs):
    staff = kwargs.get('instance')
    staff.name = unicode(staff.name)

    if staff.ch_pron is None:
        staff.ch_pron = langs.ch_pinyin(staff.name)


post_init.connect(init_staff, Staff)


class Contact(models.Model):
    staff = models.ForeignKey(Staff, related_name='contacts')
    mode = models.CharField(max_length=16)  # communication mode, "phone", "qq", "email", etc.
    value = models.CharField(max_length=128)

    EMAIL = 'email'
    QQ = 'qq'
    PHONE = 'phone'

    class Meta:
        unique_together = ('staff', 'mode', 'value')


class Department(models.Model):
    name = models.CharField(max_length=32)
    superior = models.ForeignKey('self', null=True)
    staffs = models.ManyToManyField(
        Staff,
        through='Position',
        through_fields=('department', 'staff'),
        related_name='departments',
    )

    class Meta:
        unique_together = ('name', )


class Position(models.Model):
    department = models.ForeignKey(Department)
    staff = models.ForeignKey(Staff)
    job = models.CharField(max_length=32, null=True)

    class Meta:
        unique_together = ('department', 'staff', 'job')


def sort_staff_with_ch_pron(staff_list):
    return sorted(staff_list, key=lambda x: (x.ch_pron, x.name))


def staffs_by_department(department):
    return department.staffs.all().distinct()


def search(text):
    return Staff.objects.filter(department__name__contains=text)
