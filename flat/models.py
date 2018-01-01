from __future__ import unicode_literals

from django.db import models


class Record(models.Model):
    name = models.CharField(max_length=32)
    depart1 = models.CharField(max_length=32)
    depart2 = models.CharField(max_length=32)
    extnum = models.CharField(max_length=128)
    phone = models.CharField(max_length=128)
    fax = models.CharField(max_length=128)
    mobile = models.CharField(max_length=128)
    qq = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
