# -*- coding:utf8 -*-

from __future__ import unicode_literals

from itertools import imap

from django.db import models
from django.db.models.signals import post_init
from django.contrib.auth.models import User
from rest_framework import serializers

from . import langs
from .contacts import contacts


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
    user = models.ForeignKey(User, related_name='staff', null=True)


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
        unique_together = ('name',)


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
    return Staff.objects.filter(departments__name__contains=text)


class LocaffInfo(object):
    """
    :attr id
    :attr depart1
    :attr depart2
    :attr name
    """
    contact_fields = ('email', 'qq', 'phone')

    def __init__(self, name, depart2, id=None, depart1=None, **kw):
        self.id = id
        self.name = name
        self.depart1 = depart1
        self.depart2 = depart2
        contacts = {k: v for k, v in kw.items() if k in self.contact_fields}
        self.__dict__.update(contacts)

    @property
    def _origin(self):
        return Staff.objects.get(id=self.id)

    @property
    def _exists(self):
        return (not self.id is None)

    @property
    def _contact_fields(self):
        return tuple(cf for cf in self.contact_fields if hasattr(self, cf))

    def save(self):
        if self._exists:
            self._update()
        else:
            self._create()

    def _create(self):
        s = Staff(name=self.name)
        s.save()

        for cf in self._contact_fields:
            c = Contact(staff=s, mode=cf.upper(), value=getattr(self, cf))
            c.save()

        depart = Department.objects.get(name=self.depart2)
        p = Position(staff=s, department=depart)
        p.save()

        self.id = s.id

        return self

    def _update(self):
        s = self._origin
        if self.name != s.name:
            s.name = self.name
            s.save()
        # department
        old_depart = s.departments.all()[0]
        if old_depart.name != self.depart2:
            old_p = Position.objects.get(staff=s, department=old_depart)
            new_depart = Department.objects.get(name=self.depart2)
            new_p = Position(staff=s, department=new_depart)
            old_p.delete()
            new_p.save()
        # contacts
        old_contacts = s.contacts.all()
        old_contacts = {oc.mode.lower(): oc for oc in old_contacts}
        for cf in self._contact_fields:
            if not old_contacts.has_key(cf):
                old_contacts[cf] = None
        for mode, oc in old_contacts.items():
            if oc is None:
                oc = Contact(staff=s, mode=mode.upper(), value=getattr(self, mode))
                oc.save()
            elif not hasattr(self, mode):
                oc.delete()
            else:
                if getattr(self, mode) != oc.value:
                    oc.value = getattr(self, mode)
                    oc.save()

    @classmethod
    def get(cls, operate):
        r = operate(Staff.objects
                    .prefetch_related('contacts')
                    .prefetch_related('departments__superior'))

        def consctruct_locaff_info(locaff):
            # base info
            info = {
                'id': locaff.id,
                'name': locaff.name,
            }
            # departments
            d = locaff.departments.all()[0]
            try:
                depart1 = d.superior.name
            except:
                depart1 = None
            depart2 = d.name
            if depart1 == u'北京亦庄工厂':
                depart1 = depart2
            info.update({
                'depart1': depart1,
                'depart2': depart2,
            })
            # contacts
            for c in locaff.contacts.all():
                mode = c.mode.lower()
                info.update({
                    mode: c.value
                })
            return LocaffInfo(**info)

        if hasattr(r, '__iter__'):
            return imap(consctruct_locaff_info, r)
        else:
            return consctruct_locaff_info(r)

    def delete(self):
        if self._exists:
            r = self._origin.delete()
            return r

    def to_json(self):
        return self.__dict__


# ----------------------------------------
# LocaffInfoSerializer block

def create(self, validated_data):
    if not validated_data.has_key('depart2'):
        validated_data['depart2'] = validated_data.pop('depart1')
    li = LocaffInfo(**validated_data)
    li.save()
    return li


def update(self, instance, validated_data):
    fields = tuple(['name', 'depart2'] + map(lambda x: x.key, contacts))
    fields = tuple(k for k in validated_data.keys() if k in fields)
    for f in fields:
        setattr(instance, f, validated_data[f])
    instance.save()
    return instance


binding = {
    'id': serializers.IntegerField(read_only=True),
    'name': serializers.CharField(read_only=False, max_length=32),
    'depart1': serializers.CharField(max_length=32),
    'depart2': serializers.CharField(required=False, max_length=32),

    'create': create,
    'update': update,
}

for contact in contacts:
    binding[contact.key] = serializers.CharField(required=False, max_length=128)


LocaffInfoSerializer = type(
    str('LocaffInfoSerializer'),
    (serializers.Serializer, ),
    binding)

