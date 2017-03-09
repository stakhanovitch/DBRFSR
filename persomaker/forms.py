from django import forms
from django.forms import HiddenInput
from .models import Character, Skill, CharacterSkill,Module,ModuleSkill
from math import ceil
from django.utils.translation import gettext as _


class CreationForm(forms.ModelForm):
    karma = forms.CharField(widget=forms.HiddenInput(),initial=750)
    class Meta:
        model = Character
        fields = ('name','description','ethnicity','age','sex','karma',)


        
class ModuleForm(forms.ModelForm):
    def module_assign(self, modulepk):
        moduleobject = Module.objects.get(name=modulepk)
        for tempmoduleskill in moduleobject.moduleskill_set.all():
            skillobject = Skill.objects.get(pk = tempmoduleskill.skill_id )
            if  self.instance.characterskill_set.filter(skill_id=tempmoduleskill.skill_id).exists():
                character_skill = CharacterSkill.objects.get(skill_id=skillobject.id, character_id =self.instance.id)
                character_skill.level +=  tempmoduleskill.level
                character_skill.levelmax +=  tempmoduleskill.levelmax
                character_skill.save()
            else:
                character_skill = CharacterSkill.objects.create(
                    character = self.instance,
                    skill = skillobject,
                    level = tempmoduleskill.level,
                    levelmax = tempmoduleskill.levelmax)
                tempcharacterskill = self.instance.characterskill_set.add(character_skill)
    def karma_cost(self, modulepk):
        self.instance.karma -= int(Module.objects.get(name=modulepk).karma_cost)
        self.instance.save()
        
    def save(self, *args, **kwargs):
        self.instance = super(ModuleForm, self).save(*args, **kwargs)
        data = self.cleaned_data
        for fielddata in data:
            self.module_assign(data[fielddata])
            self.karma_cost(data[fielddata])
        return self.instance
   
    TALENT = forms.ModelChoiceField(queryset = Module.objects.filter(module_bundle = '7'))
    METATYPE = forms.ModelChoiceField(queryset = Module.objects.filter(module_bundle = '1'))
    NATIONALITY = forms.ModelChoiceField(queryset = Module.objects.filter(module_bundle = '2'))
    FORMATIVE_YEARS = forms.ModelChoiceField(queryset = Module.objects.filter(module_bundle = '3'))
    TEEN_YEARS = forms.ModelChoiceField(queryset = Module.objects.filter(module_bundle = '4'))
    FURTHER_EDUCATION = forms.ModelChoiceField(queryset = Module.objects.filter(module_bundle = '5'))
    
    class Meta:
        model = Character
        fields = ('METATYPE','NATIONALITY','FORMATIVE_YEARS','TEEN_YEARS','FURTHER_EDUCATION','TALENT',)

class RealLifeForm(forms.ModelForm):
    REAL_LIFE = forms.ModelChoiceField(queryset = Module.objects.filter(module_bundle = '6'))
    class Meta:
        model = Character
        fields = ('REAL_LIFE',)

class SkillSetForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(SkillSetForm, self).clean()
        level = cleaned_data.get('level')
        levelmax = self.instance.levelmax
        skill = self.instance.skill
        print (skill,' ',level,'/',levelmax)
        if level > levelmax:
            raise forms.ValidationError (
                "You can't raise the level of your skill "+ str(skill)+ " above it's maximum level")
        
    def final_calculation(self,instance):
        instance.initiative_physical = instance.characterskill_set.get(skill__name = 'Reaction').level +  instance.characterskill_set.get(skill__name ='Intuition').level
        instance.initiative_ar = instance.characterskill_set.get(skill__name = 'Intuition').level + instance.characterskill_set.get(skill__name = 'Reaction').level
        #Character.initiative_coldsim =  
        #Character.initiative_hotsim = 
        instance.initiative_astral = instance.characterskill_set.get(skill__name ='Intuition').level*2
        instance.limit_mental = ceil((instance.characterskill_set.get(skill__name = 'Logic').level*2+instance.characterskill_set.get(skill__name = 'Intuition').level + instance.characterskill_set.get(skill__name = 'Willpower').level)/3)
        instance.limit_physical = ceil((instance.characterskill_set.get(skill__name = 'Strength').level*2+instance.characterskill_set.get(skill__name = 'Body').level+instance.characterskill_set.get(skill__name = 'Reaction').level)/3) 
        instance.limit_social =ceil((instance.characterskill_set.get(skill__name = 'Charisma').level*2+instance.characterskill_set.get(skill__name = 'Willpower').level+instance.characterskill_set.get(skill__name = 'Essence').level)/3) 

        instance.condition_physical = ceil(instance.characterskill_set.get(skill__name = 'Body').level)/2+8
        instance.condition_stun = ceil(instance.characterskill_set.get(skill__name = 'Willpower').level)/2+8
        instance.condition_overflow = instance.characterskill_set.get(skill__name = 'Body').level

        instance.living_personna_attack = instance.characterskill_set.get(skill__name = 'Charisma').level 
        instance.living_personna_dataprocessing = instance.characterskill_set.get(skill__name = 'Logic').level 
        instance.living_personna_devicerating = instance.characterskill_set.get(skill__name = 'Resonance').level 
        instance.living_personna_firewall = instance.characterskill_set.get(skill__name = 'Willpower').level 
        instance.living_personna_sleeze = instance.characterskill_set.get(skill__name = 'Intuition').level
        instance.attribute_skill_composure = instance.characterskill_set.get(skill__name = 'Charisma').level+instance.characterskill_set.get(skill__name = 'Willpower').level
        instance.attribute_skill_judgeintention =  instance.characterskill_set.get(skill__name = 'Charisma').level+instance.characterskill_set.get(skill__name = 'Intuition').level
        instance.attribute_skill_lifting =  instance.characterskill_set.get(skill__name = 'Body').level+instance.characterskill_set.get(skill__name = 'Strength').level
        instance.attribute_skill_memory =  instance.characterskill_set.get(skill__name = 'Logic').level+instance.characterskill_set.get(skill__name = 'Willpower').level

    def attribute_karma_cost(self, levelinit, characterskillinstance):
        count = 0
        errormessage = ''
        characterskillinstance = CharacterSkill.objects.get(id = characterskillinstance)
        character = Character.objects.get(id=characterskillinstance.character_id)
        skill  = Skill.objects.get(id = characterskillinstance.skill_id) 
        level_voulu = characterskillinstance.level
        grille_skill = ((1,2),(2,6),(3,12),(4,20),(5,30),(6,42),(7,56),(8,72),(9,90),(10,110),(11,132),(12,156),(13,182))
        grille_attribute = ((1,0),(2,10),(3,25),(4,45),(5,70),(6,100),(7,135),(8,175),(9,220),(10,270),(11,325))
        grille_skill = dict(grille_skill)
        grille_attribute = dict(grille_attribute)
        print('self.instance.karma_cost before: ',self.instance.karma_cost)
        if skill.skillset_choice == '99':
            self.instance.karma_cost += grille_attribute.get(level_voulu)-grille_attribute.get(levelinit)
        else:
            self.instance.karma_cost += grille_skill.get(level_voulu)-grille_skill.get(levelinit)
        print('self.instance.karma_cost after: ',self.instance.karma_cost)
        if character.karma >= self.instance.karma_cost:
            character.karma = character.karma - self.instance.karma_cost
            print('true:',errormessage,'/count',character.karma)
            
             
        else:
            print('False:',errormessage,'/count',character.karma)
            errormessage = "You don't have enought karma, it cost : "+str(self.instance.karma_cost)+" you have "+str(character.karma)+" remaining karma"
        return {'karma':character.karma,'message':errormessage}    
        
    
    def save(self, *args, **kwargs):
        levelinit = self.instance.tracker.previous('level')
        self.instance = super(SkillSetForm, self).save(*args, **kwargs)
        character = Character.objects.get(id=self.instance.character_id)
        self.final_calculation(character)
        character.karma = self.attribute_karma_cost(levelinit, self.instance.id)['karma']
        if self.attribute_karma_cost(levelinit, self.instance.id)['message']:
            self.add_error(self.attribute_karma_cost(levelinit, self.instance.id)['message'])
        character.save()
        return self.instance
        print('char=',character,character.karma)
        print('char=',character,character.karma)
        

    class Meta:
        model = CharacterSkill
        fields = ('level','karma_cost')
        #self.fields['skill'].widget.attrs['readonly'] = True
        #self.fields['levelmax'].widget.attrs['readonly'] = True

class NewSkillSetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        
        super(NewSkillSetForm, self).__init__(*args,**kwargs)
        if instance:
            self.fields['character'].initial = instance

    #define fields not already in instance's characterskills 
#    skill = forms.ModelChoiceField(queryset = Skill.objects.exclude(forms.object.name.characterskills_set()))
    

    class Meta:
        model = CharacterSkill
        fields = ('skill','level',)
        #self.fields['skill'].widget.attrs['readonly'] = True
        #self.fields['levelmax'].widget.attrs['readonly'] = True
