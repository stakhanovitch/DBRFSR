# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 10:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persomaker', '0004_skill_default'),
    ]

    operations = [
        migrations.RenameField(
            model_name='character',
            old_name='Ethnicity',
            new_name='ethnicity',
        ),
        migrations.AddField(
            model_name='character',
            name='karma',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='character',
            name='nuyen',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='skill',
            name='abstract',
            field=models.CharField(blank=True, max_length=70),
        ),
        migrations.AlterField(
            model_name='skill',
            name='description',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
