# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-22 10:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0010_circle_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='invitation_accepted',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='invitation_send',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='optional_information',
        ),
        migrations.DeleteModel(
            name='UserInfo',
        ),
    ]