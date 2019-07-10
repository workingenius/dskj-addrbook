# -*- coding: utf8 -*-
from __future__ import unicode_literals

from django.db import models


class Record(models.Model):
    name = models.CharField(max_length=32, null=True)
    depart1 = models.CharField(max_length=32, null=True)
    depart2 = models.CharField(max_length=32, null=True, blank=True)
    extnum = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=128, null=True)
    fax = models.CharField(max_length=128, null=True)
    mobile = models.CharField(max_length=128, null=True)
    qq = models.CharField(max_length=128, null=True)
    email = models.CharField(max_length=128, null=True)
    staff_num = models.CharField(max_length=128, null=True)
    job = models.CharField(max_length=128, null=True)  # 岗位


class Department(models.Model):
    name = models.CharField(max_length=32)
    superior = models.ForeignKey('self', null=True, blank=True)
    # staffs = models.ManyToManyField(
    #     Staff,
    #     through='Position',
    #     through_fields=('department', 'staff'),
    #     related_name='departments',
    # )

    class Meta:
        unique_together = ('name',)
        db_table = 'addresslist_department'

    @staticmethod
    def department_tree():
        get_sup_name = lambda d: None if d.superior is None else d.superior.name

        departs = Department.objects.all()

        by_name = {None: None}
        for d in departs:
            by_name[d.name] = d

        by_sup = {}
        for d in departs:
            sup_name = get_sup_name(d)
            if by_sup.has_key(sup_name):
                by_sup[sup_name].append(d)
            else:
                by_sup[get_sup_name(d)] = [d]

        def construct_tree(headname):
            head = by_name[headname]
            inferiors = by_sup.get(headname, [])
            return [head] + [construct_tree(d.name) for d in inferiors]

        return construct_tree(None)

    def __str__(self):
        return self.name.encode('utf8')
