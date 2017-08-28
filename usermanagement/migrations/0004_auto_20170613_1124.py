# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-13 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0003_auto_20170612_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='circle',
        ),
        migrations.AddField(
            model_name='circle',
            name='players',
            field=models.ManyToManyField(to='usermanagement.Player'),
        ),
    ]