# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-25 20:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_query_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='year',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
