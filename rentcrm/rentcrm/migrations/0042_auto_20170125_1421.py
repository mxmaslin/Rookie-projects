# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-25 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentcrm', '0041_auto_20170125_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='notes',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]