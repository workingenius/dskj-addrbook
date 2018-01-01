from __future__ import unicode_literals

from django.db import models


class Record(models.Model):
    name = models.CharField(max_length=32, null=True)
    depart1 = models.CharField(max_length=32, null=True)
    depart2 = models.CharField(max_length=32, null=True)
    extnum = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=128, null=True)
    fax = models.CharField(max_length=128, null=True)
    mobile = models.CharField(max_length=128, null=True)
    qq = models.CharField(max_length=128, null=True)
    email = models.CharField(max_length=128, null=True)
