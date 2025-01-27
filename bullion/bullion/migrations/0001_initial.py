# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-27 14:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('file', models.FileField(max_length=500, upload_to='/Users/bulrathi/Yandex.Disk.localized/Learning/Code/Commercial projects/myproject2/media')),
                ('reader_location', models.CharField(choices=[('ISUSA', 'US'), ('NONUS', 'Non-US')], max_length=5)),
                ('reader_legal_status', models.CharField(choices=[('INDIV', 'Individual'), ('ENTIT', 'Entity')], max_length=5)),
                ('is_reader_accredited', models.BooleanField(default=False, verbose_name='Investor accredited')),
            ],
        ),
        migrations.CreateModel(
            name='Investor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=150)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('notes', models.TextField(blank=True)),
                ('location', models.CharField(choices=[('ISUSA', 'US'), ('NONUS', 'Non-US')], max_length=5, verbose_name='Select your location')),
                ('legal_status', models.CharField(choices=[('INDIV', 'Individual'), ('ENTIT', 'Entity')], max_length=5, verbose_name='Select your legal status')),
                ('is_accredited', models.BooleanField(default=False, verbose_name='Are you accredited as investor?')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
