from __future__ import unicode_literals
from django.contrib import admin
from django.db import models
from datetime import timedelta, date
from django.template.defaultfilters import date as django_date

class Task(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    created_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    schedule_date = models.DateField()
    closed = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    def code_couleur_due_date(self):
        due_date = django_date(self.due_date, 'd F Y')
        counter = self.due_date - date.today()

        if self.due_date - timedelta(days=7) > date.today():
            alert = counter
            color = "green"
        elif self.due_date + timedelta(days=7) > date.today():
            alert = "today"
            color = "orange"
        else:
            alert = "too late"
            color = "red"
        return '<span style=color:%s>%s</span>' % (color, alert)
    code_couleur_due_date.allow_tags = True

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name','code_couleur_due_date')
