# -*-coding:utf-8 -*-
from django.core.exceptions import ValidationError
from django import forms
from django.forms import HiddenInput, CheckboxSelectMultiple
from .models import *
from math import ceil
from django.utils.translation import gettext as _
from itertools import chain

#//////////////////////////////////////////////////////////////////#
class CharacterCreationForm(forms.ModelForm):
    karma = forms.CharField(widget=forms.HiddenInput(), initial=750)
    def __init__(self, *args, **kwargs):
        player = kwargs.pop('player', None)
        campaign = kwargs.pop('campaign', None)
        super(CharacterCreationForm, self).__init__(*args, **kwargs)
        self.initial['player'] = player
        self.fields['player'].widget = HiddenInput()
        self.initial['campaign'] = campaign
        self.fields['campaign'].widget = HiddenInput()
    class Meta:
        model = Character
        fields = ('name','image','karma','player','campaign')


class ModuleForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(ModuleForm, self).__init__(*args,**kwargs)
        module = kwargs.pop('module', None)
        character = kwargs.pop('character', None)
        self.fields['character'].widget = HiddenInput()
        self.fields['module'].widget = HiddenInput()
        self.fields['charactermoduleoption'].widget = forms.RadioSelect(choices=self.fields['charactermoduleoption'].choices)

    def module_assign(self):
        #print('module_assign')
        #print('try',self.cleaned_data['charactermoduleoption'])
        character = self.instance.character
        if self.cleaned_data['charactermoduleoption']:
            option_moduleskill_set = self.instance.module.options.get(name = self.cleaned_data['charactermoduleoption']).moduleskill_set.all()
            option_quality_set = Quality.objects.filter(module = self.cleaned_data['charactermoduleoption'])
        else:
            option_moduleskill_set = ''
            option_quality_set = ''
        #print(option_moduleskill_set)
        #je crée quand même la relation
        if len(CharacterModule.objects.filter(character = character, module = self.instance.module))<=1:
            for tempmoduleskill in chain(self.instance.module.moduleskill_set.all(),option_moduleskill_set):
                character_skill = CharacterSkill.objects.filter(skill = Skill.objects.get(pk = tempmoduleskill.skill_id) , character = self.instance.character).first()
                if  character_skill :
                    character_skill.level +=  tempmoduleskill.level
                    character_skill.levelmax +=  tempmoduleskill.levelmax
                    character_skill.save()
                else:
                    character_skill = CharacterSkill.objects.create(
                        character = character,
                        skill = Skill.objects.get(pk = tempmoduleskill.skill_id),
                        level = tempmoduleskill.level,
                        levelmax = tempmoduleskill.levelmax)
                    tempcharacterskill = character.characterskill_set.add(character_skill)
        for quality in chain(Quality.objects.filter(module = self.instance.module),option_quality_set):
            quality.character.add(character)

    def karma_cost(self):
        module = Module.objects.get(pk = self.instance.module_id)
        character = Character.objects.get(pk = self.instance.character_id)
        character.karma -= int(module.karma_cost)
        character.save()

    def save(self, *args, **kwargs):
        self.instance = super(ModuleForm, self).save(*args, **kwargs)
        if self.cleaned_data['module']:
            self.module_assign()
            self.karma_cost()
        #self.instance.save()
        return self.instance

    class Meta:
        model = CharacterModule
        fields = ('module','character','charactermoduleoption')



class CharacterTraitForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(CharacterTraitForm, self).__init__(*args,**kwargs)
        character = kwargs.pop('character', None)
        trait = kwargs.pop('trait', None)
        self.fields['character'].widget = HiddenInput()
        self.fields['trait'].widget = HiddenInput()

    def clean(self):
        cleaned_data = super(CharacterTraitForm, self).clean()
        if cleaned_data['trait'].karma_cost + cleaned_data['character'].current_quality_sum() >= cleaned_data['character'].max_quality:
            raise ValidationError(
                "You can't add %(trait)s to your character %(character)s, you are exceeding the maximum point of traits",
                code='exceeding_maximum_traits',
                params={
                    'trait': cleaned_data['trait'].name,
                    'character':cleaned_data['character'].name,
                },
)



    class Meta:
        model = CharacterTrait
        fields = ('trait','character',)


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
