# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-08 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bullion', '0004_auto_20161201_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='investor',
            name='email',
            field=models.EmailField(default='zapzarap@yandex.ru', max_length=254),
            preserve_default=False,
        ),
    ]
