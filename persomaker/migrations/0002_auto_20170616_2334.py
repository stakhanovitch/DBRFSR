# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-16 21:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persomaker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='abstract',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
