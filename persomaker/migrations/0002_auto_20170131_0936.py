# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 08:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('persomaker', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characterskill',
            name='caracter',
        ),
        migrations.AddField(
            model_name='characterskill',
            name='character',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='persomaker.Character'),
        ),
        migrations.AddField(
            model_name='characterskill',
            name='level',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='characterskill',
            name='levelmax',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='characterskill',
            name='skill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='persomaker.Skill'),
        ),
    ]
