# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-06 10:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentcrm', '0009_auto_20161106_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='apartment',
            name='occupied',
            field=models.BooleanField(default=False),
        ),
    ]