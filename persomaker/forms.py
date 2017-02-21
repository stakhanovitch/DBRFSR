from django import forms
from django.forms import HiddenInput
from .models import Character, Skill, CharacterSkill,Module,ModuleSkill


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
class SkillForm():
    pass

class SkillSetForm(forms.ModelForm):
        class Meta:
            model = CharacterSkill
            fields = ('skill','level','levelmax','character')
            #self.fields['skill'].widget.attrs['readonly'] = True
            #self.fields['levelmax'].widget.attrs['readonly'] = True

class NewSkillSetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super(NewSkillSetForm, self).__init__(*args,**kwargs)
        #self.fields["newskillset"].queryset = Skill.objects.all()
#        if instance:
#            self.fields['character'].initial = instance
            
    
    def clean_skill(self):
        if self.instance:
            return self.instance.skill
        else: 
            return self.fields['skill']

    def get_form_kwargs(self, index):
        kwargs = super(NewSkillSetForm, self).get_form_kwargs(index)
        kwargs['instance'] = index
        return kwargs

    class Meta:
        model = CharacterSkill
        fields = ('skill','level','character')
        #self.fields['skill'].widget.attrs['readonly'] = True
        #self.fields['levelmax'].widget.attrs['readonly'] = True
