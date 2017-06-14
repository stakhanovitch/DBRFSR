# -*-coding:utf-8 -*-
from django.contrib import admin

from .models import Character,Skill,CharacterSkill,Module,ModuleSkill,CharacterModule, Action, Modifier,Quality,SkillSpecialisation,Obj,Stat,ObjStat,CharacterObj

admin.site.register(Character)
admin.site.register(Skill)
admin.site.register(SkillSpecialisation)
admin.site.register(CharacterSkill)
admin.site.register(CharacterModule)
admin.site.register(ModuleSkill)
admin.site.register(Module)
admin.site.register(Action)
admin.site.register(Modifier)
admin.site.register(Quality)

admin.site.register(Obj)
admin.site.register(Stat)
admin.site.register(ObjStat)
admin.site.register(CharacterObj)
# Register your models here.
