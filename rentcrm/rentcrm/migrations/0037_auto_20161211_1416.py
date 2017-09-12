# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-11 14:16
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentcrm', '0036_contract_main_tenant_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='main_tenant_name',
        ),
        migrations.AlterField(
            model_name='apartment',
            name='rent_legal',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='leaserenewaloffer',
            name='rent_legal_one_year',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='leaserenewaloffer',
            name='rent_legal_two_years',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
    ]