from django.contrib import admin

from .models import Character,Skill,CharacterSkill,Module,ModuleSkill

admin.site.register(Character)
admin.site.register(Skill)
admin.site.register(CharacterSkill)
admin.site.register(Module)
admin.site.register(ModuleSkill)    
# Register your models here.
