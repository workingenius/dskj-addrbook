# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-01-01 03:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('depart1', models.CharField(max_length=32)),
                ('depart2', models.CharField(max_length=32)),
                ('extnum', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=128)),
                ('fax', models.CharField(max_length=128)),
                ('mobile', models.CharField(max_length=128)),
                ('qq', models.CharField(max_length=128)),
                ('email', models.CharField(max_length=128)),
            ],
        ),
    ]
