from django.contrib import admin
from .models import Task,TaskAdmin

admin.site.register(Task,TaskAdmin)
