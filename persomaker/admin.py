from django.contrib import admin

from .models import Character,Skill,CharacterSkill

admin.site.register(Character)
admin.site.register(Skill)
admin.site.register(CharacterSkill)
# Register your models here.
