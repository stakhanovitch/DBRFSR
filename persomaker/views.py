# -*-coding:utf-8 -*-
import collections
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from itertools import chain
from django.urls import reverse
from django.views import generic
from math import ceil
from .forms import CreationForm,ModuleForm,SkillCreateForm,CharacterSkillModifyForm
from django.forms import formset_factory,modelformset_factory,inlineformset_factory
from functools import partial, wraps

from persomaker.models import Character,Skill,CharacterSkill,Module,ModuleSkill,CharacterModule,Action,Modifier,Quality,SkillSpecialisation,Obj,Stat,ObjStat,CharacterObj
from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.template.defaulttags import register

from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

#///////////   nouvelle version persomaker 29/03   ////////////////#
def character_creation(request):
    form = CreationForm(request.POST)
    user = User.objects.get (id = request.user.id)
    if form.is_valid():
        character = form.save()
        return redirect('persomaker:module', 0, character.id)
    else:
        form = CreationForm(initial={'player':user})
        form.fields['player'].widget = HiddenInput()
    return render(request, 'character/create.html', {'form': form,})

def character_profile(request,pk):
    instance = Character.objects.get (id = pk)
    skills = instance.characterskill_set.filter(skill__skillset_choice='96',).order_by('skill__skillset_choice')
    calculated = instance.characterskill_set.filter(skill__skillset_choice='94',)
    objset = instance.characterobj_set.all().filter(is_equiped = True)
    print(instance.physical_condition())
    return render(request, 'character/profile.html',
    {
    'instance':instance,
    'objset':objset,
    'calculated':calculated,
    'skills':skills,
    })

def character_inventory(request, charpk):
    """
    give the list of all the obj in the character inventory and allow a character to manage the obj it need (sell/buy/equip)
    """
    instance = Character.objects.get(id=charpk)
    obj = Obj.objects.filter(characterobj__character = instance.id)
    OBJECT_CATEGORY = {
                        '01': 'Weapon',
                        '02': 'Armor',
                        '03':'Commlink'}
    return render(request, 'character/list.html',
    {'obj':obj,
    'OBJECT_CATEGORY':OBJECT_CATEGORY,
    'instance':instance,
    })


def action_effect(request,objectpk,actionpk):
    print('first prout')
    if request.method =="POST":
        instance = Character.objects.get(id=CharacterWeapon.objects.get(id=objectpk).character_id)
        current_object = CharacterWeapon.objects.get(id=objectpk)
        current_action = Action.objects.get(id=actionpk)
        #for modifier in current_action.modifier_effect.all()

        return redirect('persomaker:character_profile', instance.id)


def module_choice_form(request,pk,modulepk):
    form = ModuleForm(request.POST)
    user = User.objects.get (id = request.user.id)
    instance = Character.objects.get (id = pk)
    module_choice = {
                    '0':'Metatype',
                    '1':'Nationality',
                    '2':'Formative years',
                    '3':'Teen years',
                    '4':'Further education',
                    '5':'Real life',
                    '6':'Talent',
                    }

    module_bundle = Module.objects.filter(module_bundle = modulepk)
    if form.is_valid():
        form.save()
        nextpage = int(modulepk) + 1
        if nextpage < 6:
            return redirect('persomaker:module', nextpage, instance.id)
        else:
            return redirect('persomaker:skill_list', instance.id)
    else:
        if CharacterModule.objects.filter(character = instance,module_id__in = module_bundle):
            pass
        else:
            form = ModuleForm(initial={'character':instance})
        #
        form.fields['module'].label = "What's your " + module_choice[modulepk]
        form.fields['module'].queryset = module_bundle
        form.fields['character'].widget = HiddenInput()
    return render(request, 'character/create.html', {'form': form,})

def skill_list(request,pk):
    user = User.objects.get(id = request.user.id)
    instance = Character.objects.get (id = pk)
    attribute_set = instance.characterskill_set.filter(skill__skillset_choice ='99').order_by('skill__context')
    skill_set = instance.characterskill_set.filter(skill__skillset_choice = '96').order_by('skill__skillset_choice')
    skill_category = Skill.objects.filter(characterskill__character = instance.pk,).exclude(skillset_choice='99').distinct()
    templist = []
    for tempcat in skill_category:
        if tempcat.skillgroup:
            skill_group = Skill.objects.get(id = tempcat.skillgroup_id)
            if skill_group not in templist:
                templist.append(skill_group)

    knowledge_category = {
                        '90':'Academic knowledge',
                        '91':'Interests knowledge',
                        '92':'Professional knowledge',
                        '93':'Street knowledge',
                        '98':'Language',
                        }

    knowledge_set = instance.characterskill_set.filter(skill__skillset_choice__in = knowledge_category).order_by('skill__skillset_choice')
    qualities = Quality.objects.filter(character = instance)
    print(qualities)
    return render(request, 'character/manage_skill.html',
    {
    'instance':instance,
    'attribute_set': attribute_set,
    'skill_set': skill_set,
    'skill_category':templist,
    'knowledge_category':knowledge_category,
    'knowledge_set':knowledge_set,
    'qualities':qualities,
        })

def skill_add(request,pk,skillfilter):
    skill_filter = Skill.objects.filter(skillset_choice=skillfilter)
    form = SkillCreateForm(request.POST)
    user = User.objects.get (id = request.user.id)
    instance = Character.objects.get (id = pk)
    if form.is_valid():
        form.save()
        return redirect('persomaker:skill_list', instance.id)
    else:
        skills = skill_filter.exclude(characters = instance)
        form = SkillCreateForm(initial={'character':instance})
        form.fields['skill'].queryset = skills
        form.fields['character'].widget = HiddenInput()
    return render(request, 'character/create_skill.html',
    {
    'skill':skill_filter,
    'instance':instance,
    'form': form,})

def skill_update(request,skillpk,instancepk):
    user = User.objects.get (id = request.user.id)
    instance = Character.objects.get (id = instancepk)
    skill = CharacterSkill.objects.get(id = skillpk)
    if request.method == "POST":
        form = SkillModifyForm(request.POST,instance = skill,)
        print (skill)
        if form.is_valid():
            form.save()
            return redirect('persomaker:skill_list', instance.id)
    else:
        form = SkillModifyForm(instance = skill,)
        form.fields['specialisations'].queryset = SkillSpecialisation.objects.filter(skill = skill.skill)
        form.fields['skill'].widget = HiddenInput()
        form.fields['character'].widget = HiddenInput()
        form.fields['levelmax'].widget = HiddenInput()
    return render(request, 'character/update_skill.html',
    {'instance':instance,
    'skill':skill,
    'form': form,})
class CharacterSkillDelete(DeleteView):
    model = CharacterSkill
    def get_success_url(self):
        character = self.object.character
        return reverse('persomaker:skill_list', args=[character.id])

class CharacterSkillDetailView(DetailView):
    model = CharacterSkill
    def get_context_data(self,**kwargs):
        context = super(CharacterSkillDetailView, self).get_context_data(**kwargs)
        form = CharacterSkillModifyForm( instance = self.object)
        context['form'] = form
        return context
    def post(self, request, *args,**kargs):
        object = self.get_object()
        print(type(object))
        form = CharacterSkillModifyForm(self.request.POST, instance = object)
        if form.is_valid():
            print('prout')
            form.save()
            return redirect('persomaker:skill_list', object.character_id)
        else:
            print('pas prout')
            return render(request, 'persomaker/characterskill_detail.html',
            {'form': form,})
def object_view(request,id):
    """
    give a detailed view of the requested obj
    """
    obj = Obj.objects.get(id = id)
    objstat = ObjStat.objects.filter(obj=obj)
    return render(request, 'character/view.html',
    {'obj':obj,
    'objstat':objstat,
    })

def object_list(request,id):
    """
    give the list of all the obj and allow a character to manage the obj it need (sell/buy)
    """
    obj = Obj.objects.all()
    instance = Character.objects.get(id = id)
    OBJECT_CATEGORY = {
                        '01': 'Weapon',
                        '02': 'Armor',
                        '03':'Commlink'}
    return render(request, 'character/list.html',
    {'obj':obj,
    'OBJECT_CATEGORY':OBJECT_CATEGORY,
    'instance':instance,
    })

def object_buy(request,charpk,objpk):
    if request.method =="POST":
        characterobj = CharacterObj.objects.create(obj_id=objpk,character_id = charpk)
        characterobj.save()
        return redirect('persomaker:object_list', characterobj.character.id)

def object_sell(request,charpk,objpk):
    if request.method =="POST":
        characterobj = CharacterObj.objects.filter(obj_id=objpk,character_id = charpk).first()
        print(characterobj)
        CharacterObj.delete(characterobj)
        return redirect('persomaker:object_list', charpk)

def object_equip(request,charobjpk):
    if request.method =="POST":
        characterobj = CharacterObj.objects.get(id = charobjpk)
        characterobj.equiped = True
        characterobj.save()
        return redirect('persomaker:object_list', characterobj.character.id)


def skill_view(request,id):
    pass

def skill_delete(request,pk):
    if request.method =="POST":
        characterskilltodelete = CharacterSkill.objects.get(id=pk)
        instance = Character.objects.get(id = characterskilltodelete.character_id)
        characterskilltodelete.delete()
        return redirect('persomaker:skill_list', instance.id)

def skill_final_calculation(request,pk):
        instance = Character.objects.get(id=pk)
        # pas de refactoring trouvé
        #Physical initiative
        characterskill = CharacterSkill.objects.filter(skill__name = 'Physical initiative', character = instance)
        level_value = CharacterSkill.objects.get(skill__name = 'REACTION', character = instance).level + CharacterSkill.objects.get(skill__name = 'ESSENCE', character = instance).level
        if characterskill:
            characterskill = CharacterSkill.objects.get(skill__name = 'Physical initiative', character = instance)
            characterskill.level = level_value
            characterskill.levelmax = level_value
            characterskill.save()
        else:
            characterskill = CharacterSkill(character = instance, skill = Skill.objects.get(name = 'Physical initiative'), level = level_value, levelmax = level_value)
            characterskill.save()
        #Mental Limit
        characterskill = CharacterSkill.objects.filter(skill__name = 'Mental Limit', character = instance)
        print (characterskill)
        level_value = ceil(float(CharacterSkill.objects.get(skill__name = 'LOGIC', character = instance).level*2 + CharacterSkill.objects.get(skill__name = 'INTUITION', character = instance).level + CharacterSkill.objects.get(skill__name = 'WILLPOWER', character = instance).level)/3)
        if characterskill:
            characterskill = CharacterSkill.objects.get(skill__name = 'Mental Limit', character = instance)
            characterskill.level = level_value
            characterskill.levelmax = level_value
            characterskill.save()
        else:
            test = CharacterSkill(character = instance, skill = Skill.objects.get(name = 'Mental Limit'), level = level_value, levelmax = level_value)
            test.save()
        #Physical Limit
        characterskill = CharacterSkill.objects.filter(skill__name = 'Physical Limit', character = instance)
        print (characterskill)
        level_value = ceil(float((CharacterSkill.objects.get(skill__name = 'STRENGTH', character = instance).level*2 + CharacterSkill.objects.get(skill__name = 'BODY', character = instance).level + CharacterSkill.objects.get(skill__name = 'REACTION', character = instance).level)/3))
        print(level_value)
        level_value = level_value/3
        print(level_value)
        level_value = ceil(level_value)
        print(level_value)
        if characterskill:
            characterskill = CharacterSkill.objects.get(skill__name = 'Physical Limit', character = instance)
            characterskill.level = level_value
            characterskill.levelmax = level_value
            characterskill.save()
        else:
            test = CharacterSkill(character = instance, skill = Skill.objects.get(name = 'Physical Limit'), level = level_value, levelmax = level_value)
            test.save()
        #Social Limit
        characterskill = CharacterSkill.objects.filter(skill__name = 'Social Limit', character = instance)
        print (characterskill)
        level_value = ceil(float(CharacterSkill.objects.get(skill__name = 'CHARISMA', character = instance).level*2 + CharacterSkill.objects.get(skill__name = 'WILLPOWER', character = instance).level + CharacterSkill.objects.get(skill__name = 'ESSENCE', character = instance).level)/3)
        if characterskill:
            characterskill = CharacterSkill.objects.get(skill__name = 'Social Limit', character = instance)
            characterskill.level = level_value
            characterskill.levelmax = level_value
            characterskill.save()
        else:
            test = CharacterSkill(character = instance, skill = Skill.objects.get(name = 'Social Limit'), level = level_value, levelmax = level_value)
            test.save()
        #Physical condition
        characterskill = CharacterSkill.objects.filter(skill__name = 'Physical condition', character = instance)
        print (characterskill)
        level_value = ceil(float(CharacterSkill.objects.get(skill__name = 'BODY', character = instance).level)/2 + 8)
        if characterskill:
            characterskill = CharacterSkill.objects.get(skill__name = 'Physical condition', character = instance)
            characterskill.levelmax = level_value
            characterskill.save()
        else:
            test = CharacterSkill(character = instance, skill = Skill.objects.get(name = 'Physical condition'), level = level_value, levelmax = level_value)
            test.save()
        #Stun condition
        characterskill = CharacterSkill.objects.filter(skill__name = 'Stun condition', character = instance)
        print (characterskill)
        print (float(CharacterSkill.objects.get(skill__name = 'WILLPOWER', character = instance).level)/2)

        level_value = ceil(float(CharacterSkill.objects.get(skill__name = 'WILLPOWER', character = instance).level)/2 + 8)
        if characterskill:
            characterskill = CharacterSkill.objects.get(skill__name = 'Stun condition', character = instance)
            characterskill.levelmax = level_value
            characterskill.save()
        else:
            test = CharacterSkill(character = instance, skill = Skill.objects.get(name = 'Stun condition'), level = level_value, levelmax = level_value)
            test.save()
        #Overflow
        characterskill = CharacterSkill.objects.filter(skill__name = 'Overflow', character = instance)
        print (characterskill)
        level_value = CharacterSkill.objects.get(skill__name = 'BODY', character = instance).level
        if characterskill:
            characterskill = CharacterSkill.objects.get(skill__name = 'Overflow', character = instance)
            characterskill.level = level_value
            characterskill.levelmax = level_value
            characterskill.save()
        else:
            test = CharacterSkill(character = instance, skill = Skill.objects.get(name = 'Overflow'), level = level_value, levelmax = level_value)
            test.save()

        return redirect('persomaker:character_profile', instance.id)

"""
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
"""
#//////////////////////////////////////////////////////////////////#
class IndexView(generic.ListView):
    template_name = 'persomaker/index.html'
    context_object_name = 'character_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Character.objects.order_by('-name')[:50]

def character_creation2(request, pk):
    template = loader.get_template('persomaker/creation.html')
    character = get_object_or_404(Character, pk=pk)
    #set de Skills/attributs
    attribute_set = character.characterskill_set.filter(skill__skillset_choice='99').order_by('skill__name')
    skill_set = character.characterskill_set.exclude(skill__skillset_choice='99').order_by('skill__name')
    personnal_data = {'name':character.name,}
    currency = {'karma':character.karma,
                'nuyen':character.nuyen,
    }
    #calcul finaux
    #final_calculation(character)
    context = {'pk':pk}
    return render(request, 'persomaker/creation.html', {
            'personnal_data':personnal_data,
            'character': character,
            'attribute_set':attribute_set,
            'skill_set':skill_set,
            'currency':currency,
        })



def character_creation2(request):
    form = CreationForm(request.POST)
    if form.is_valid():
        character = form.save()
        return redirect('persomaker:character_module', character.id)
    else:
        form = CreationForm()
    return render(request,
                  'persomaker/character-creation.html',
                  {'form': form}
    )

def character_module(request,pk):
    instance = get_object_or_404(Character, pk=pk)
    formset = formset_factory(RealLifeForm,)
    form = ModuleForm(request.POST, instance=instance)
    if form.is_valid():

        character = form.save()
        return redirect('persomaker:character_skillset', instance.id)
    else:
        form = ModuleForm()
        return render(request,
                      'persomaker/character-module.html',
                      {'form': form,'formset':formset},
        )

def character_skillset(request,pk):
    instance = get_object_or_404(Character, pk=pk)
    SkillSetFormSet = modelformset_factory(CharacterSkill,fields=('level',), form = SkillSetForm, exclude=None, extra=0)
    qset = instance.characterskill_set.all()
    currentskillformset = SkillSetFormSet(queryset = qset,prefix='characterskill')
    if request.method == 'POST':
        #deal with posting the data
        currentskillformset = SkillSetFormSet(request.POST, prefix='characterskill')
        if currentskillformset.is_valid():
        #if it is not valid then the "errors" will fall through and be returned
            currentskillformset.save()
#            final_calculation(instance)
#            instance.save()
            return render(request, 'persomaker/character-skillset.html', {
                'currentskillformset':currentskillformset,
                'character':instance,
           } )
        else:
            return render(request, 'persomaker/character-skillset.html', {
                'currentskillformset':currentskillformset,
                'character':instance,
            })


    return render(request, 'persomaker/character-skillset.html', {
        'currentskillformset':currentskillformset,
        'character':instance,

    })


def character_newskillset(request,pk):
    instance = get_object_or_404(Character, pk = pk)
    NewSkillForm
    #test = instance.characterskill_set.all().values('skill_id')
    #qset = Skill.objects.exclude(test)

    formset = newskillsetformset(instance = instance, prefix='newskill')
    if request.method == 'POST':
        formset = newskillsetformset(request.POST, prefix='newskill',instance = instance)
        if formset.is_valid():
            formset.save()

    return render(request, 'persomaker/character-newskillset.html', {
        'formset': formset,
    })
