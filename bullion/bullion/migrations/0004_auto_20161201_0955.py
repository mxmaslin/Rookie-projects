# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-01 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bullion', '0003_auto_20161130_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investor',
            name='ip_address',
            field=models.GenericIPAddressField(default='127.0.0.1'),
        ),
    ]
