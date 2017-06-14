# -*-coding:utf-8 -*-
from django import forms
from django.forms import HiddenInput
from .models import Character, Skill, CharacterSkill,Module,ModuleSkill,CharacterModule,Quality,SkillSpecialisation
from math import ceil
from django.utils.translation import gettext as _

#//////////////////////////////////////////////////////////////////#
class CreationForm(forms.ModelForm):
    karma = forms.CharField(widget=forms.HiddenInput(), initial=750)
    class Meta:
        model = Character
        fields = ('name','karma','player')


class ModuleForm(forms.ModelForm):
    def module_assign(self):
        moduleobject = self.instance.module
        character = self.instance.character
        #je crée quand même la relation
        if len(CharacterModule.objects.filter(character = character, module = self.instance.module))<=1:
            for tempmoduleskill in moduleobject.moduleskill_set.all():
                tempskill = Skill.objects.get(pk = tempmoduleskill.skill_id)
                character_skill = CharacterSkill.objects.filter(skill_id = tempskill.id , character_id = character.pk)
                if  character_skill :
                    character_skill.level +=  tempmoduleskill.level
                    character_skill.levelmax +=  tempmoduleskill.levelmax
                    character_skill.save()
                else:
                    character_skill = CharacterSkill.objects.create(
                        character = character,
                        skill = tempskill,
                        level = tempmoduleskill.level,
                        levelmax = tempmoduleskill.levelmax)
                    tempcharacterskill = character.characterskill_set.add(character_skill)
        for quality in Quality.objects.filter(module = moduleobject):
            print (quality)
            quality.character.add(character)

    def karma_cost(self):
        module = Module.objects.get(pk = self.instance.module_id)
        character = Character.objects.get(pk = self.instance.character_id)
        character.karma -= int(module.karma_cost)
        character.save()
    def save(self, *args, **kwargs):
        self.instance = super(ModuleForm, self).save(*args, **kwargs)
        data = self.cleaned_data
        for fielddata in data:
            if fielddata == 'module':
                self.module_assign()
                self.karma_cost()
        return self.instance
    class Meta:
        model = CharacterModule
        fields = ('module','character')

class SkillCreateForm(forms.ModelForm):
    class Meta:
        model = CharacterSkill
        fields = ('skill','level','character',)

class CharacterSkillModifyForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(CharacterSkillModifyForm, self).__init__(*args,**kwargs)
        self.fields['skill'].widget = HiddenInput()
        self.fields['character'].widget = HiddenInput()
        self.fields['levelmax'].widget = HiddenInput()
        """
        if 'specialisations' in self.initial:
            self.fields['specialisations'].queryset = SkillSpecialisation.objects.filter(skill = self.initial['skill'])
            if not self.fields['specialisations'].queryset:
                self.fields['specialisations'].widget = HiddenInput()
        """
    class Meta:
        model = CharacterSkill
        fields = ('character','level','skill','levelmax','specialisations')


#//////////////////////////////////////////////////////////////////#
