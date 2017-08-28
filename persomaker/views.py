# -*-coding:utf-8 -*-
import collections
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from itertools import chain
from django.urls import reverse
from django.views import generic
from math import ceil
from persomaker.forms import *
from persomaker.models import *

#from django.forms import formset_factory,modelformset_factory,inlineformset_factory
from functools import partial, wraps


from django.contrib.auth.models import User
from django.forms import HiddenInput
from django.template.defaulttags import register

from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView, CreateView, ModelFormMixin
from django.views.generic import FormView,ListView
from usermanagement.views import LoginRequiredMixin

from django.urls import reverse_lazy
from django.template import Context
from usermanagement.models import Circle

#///////////////////////////////////////////////////////////////////////////////
#Views related to Character Model
class CharacterDelete(LoginRequiredMixin, DeleteView):
    model = Character
    template_name = "user/simple_delete.html"
    success_url = reverse_lazy('usermanagement:user_profile')

class CreateCharacterView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CharacterCreationForm
    template_name = 'persomaker/create_character.html'

    def get_context_data(self, **kwargs):
        # I need the campaign ID for the submenu
        context = super(CreateCharacterView, self).get_context_data(**kwargs)
        context['campaign'] = Circle.objects.get(slug = self.kwargs['campaign_slug'])
        return context

    def get_success_url(self):
        return reverse('persomaker:module_list', args=[self.object.id])

    def get_form_kwargs(self):
        kwargs = super(CreateCharacterView, self).get_form_kwargs()
        kwargs['player'] = self.request.user # pass the 'user' in kwargs
        try:
            kwargs['campaign'] = Circle.objects.get(slug = self.kwargs['campaign_slug'])
        except Exception as e:
            pass
        return kwargs

class UpdateCharacterView(LoginRequiredMixin, UpdateView):
    model = Character
    pk_url_kwarg = "characterpk"
    form_class = CharacterCreationForm
    template_name = 'persomaker/create_character.html'

    def get_context_data(self, **kwargs):
        # I need the campaign ID for the submenu
        context = super(UpdateCharacterView, self).get_context_data(**kwargs)
        context['campaign'] = Circle.objects.get(slug = self.kwargs['campaign_slug'])
        context['character'] = Character.objects.get(pk = self.kwargs['characterpk'])
        return context

    def get_success_url(self):
        return reverse('persomaker:module_list', args=[self.object.id])
    def get_form_kwargs(self):
        kwargs = super(UpdateCharacterView, self).get_form_kwargs()
        kwargs['player'] = self.request.user # pass the 'user' in kwargs
        try:
            kwargs['campaign'] = Circle.objects.get(slug = self.kwargs['campaign_slug'])
        except Exception as e:
            pass
        return kwargs

class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = 'persomaker/character_view.html'

#///////////////////////////////////////////////////////////////////////////////
#Views related to Campaign Model (former circle)

class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Circle
    slug_url_kwarg = "campaign_slug"
    slug_field = "slug"
    template_name = 'persomaker/campaign_view.html'
    def get_context_data(self, **kwargs):
        # I need the campaign ID for the submenu
        context = super(CampaignDetailView, self).get_context_data(**kwargs)
        context['campaign'] = Circle.objects.get(slug = self.kwargs['campaign_slug'])
        try:
            context['character'] = Character.objects.get(pk = self.kwargs['characterpk'])
        except Exception as e:
            pass
        return context
#///////////////////////////////////////////////////////////////////////////////
#Views related to Module & CharacterModule Models

class CharacterModuleListView(LoginRequiredMixin, ListView):
    model = Module
    template_name = 'persomaker/module_list.html'
    def get_context_data(self, **kwargs):
        # Get queryset by category item
        context = super(CharacterModuleListView, self).get_context_data(**kwargs)
        categories = (
                            ('0','Metatype'),
                            ('1','Talent'),
                            ('2','Nationality'),
                            ('3','Formative years'),
                            ('4','Teen years'),
                            ('5','Further education'),
                            ('6','Real life'),
                            )
        category2 = {}
        charactercategory2 = {}
        for value in categories:
            item = {value[1] : Module.objects.filter(module_bundle = value[0])}
            category2.update(item)
            item2 = {value[1] : CharacterModule.objects.filter(module__module_bundle = value[0], character_id = self.kwargs['characterpk'])}
            charactercategory2.update(item2)
        context['categories'] = category2
        context['charactercategories'] = charactercategory2
        if 'characterpk' in self.kwargs:
            context['character'] = get_object_or_404(Character, pk=self.kwargs['characterpk'])
        return context

    def get_queryset(self):
        object_list = Module.objects.all()
        if "categorypk" in self.kwargs:
            object_list = Module.objects.filter(module_bundle = self.kwargs['categorypk'])
        return object_list

class ModuleDetailView(LoginRequiredMixin, DetailView):
    model = Module
    template_name = 'persomaker/module_view.html'
    success_url = reverse_lazy('persomaker:module_list')

    def get_context_data(self, **kwargs):
        context = super(ModuleDetailView, self).get_context_data(**kwargs)
        if 'pk' in self.kwargs:
            context['item'] = get_object_or_404(Module, pk=self.kwargs['pk'])
        if 'characterpk' in self.kwargs:
            context['character'] = get_object_or_404(Character, pk=self.kwargs['characterpk'])
        try:
            instance = CharacterModule.objects.get(character = get_object_or_404(Character, pk=self.kwargs['characterpk']),module = get_object_or_404(Module, pk=self.kwargs['pk']))
            form = ModuleForm(instance = instance)
        except Exception as e:
            form = ModuleForm(
            initial = { 'character' : get_object_or_404(Character, pk=self.kwargs['characterpk']),'module':get_object_or_404(Module, pk=self.kwargs['pk']),})
        context['form'] = form
        return context

    def post(self, request, *args,**kargs):
        object = self.get_object()
        try:
            instance = CharacterModule.objects.get(character = get_object_or_404(Character, pk=self.kwargs['characterpk']),module = get_object_or_404(Module, pk=self.kwargs['pk']))
            form = ModuleForm(self.request.POST, instance = instance)
        except Exception as e:
            form = ModuleForm(self.request.POST,
            initial = { 'character' : get_object_or_404(Character, pk=self.kwargs['characterpk']),'module':get_object_or_404(Module, pk=self.kwargs['pk']),})
        if form.is_valid():
            form.save()
            return redirect('persomaker:module_list', self.kwargs['characterpk'])
        else:
            return render(request, 'persomaker/module_view.html',
            {'form': form,})

class CharacterModuleDelete(LoginRequiredMixin, DeleteView):
    model = CharacterModule
    template_name = "persomaker/characterskill_delete.html"
    def get_success_url(self):
        character = self.object.character
        success_url = reverse('persomaker:module_list', args=[character.id])
        return success_url

#///////////////////////////////////////////////////////////////////////////////
#views related to Trait & CharacterTraits Model

class TraitListView(LoginRequiredMixin, ListView):
    model = Trait
    template_name = 'persomaker/trait_list.html'
    def get_queryset(self):
        # dans l'attente d'un refactoring plus joli
        if "category_slug" in self.kwargs:
            if self.kwargs['category_slug'] == "quality":
                cat = '01'
            elif self.kwargs['category_slug'] == "default":
                cat = '02'
            else:
                cat =""
            object_list = Trait.objects.filter(quality_type = cat)
            return object_list
    def get_context_data(self, **kwargs):
        # I need the campaign ID for the submenu
        context = super(TraitListView, self).get_context_data(**kwargs)
        context['character'] = Character.objects.get(pk = self.kwargs['characterpk'])
        return context

class CharacterTraitListView(LoginRequiredMixin, ListView):
    model = CharacterTrait
    template_name = 'persomaker/charactertrait_list.html'
    def get_queryset(self):
        if "characterpk" in self.kwargs:
            object_list = CharacterTrait.objects.filter(character = self.kwargs['characterpk'])
            return object_list
    def get_context_data(self, **kwargs):
        # I need the campaign ID for the submenu
        context = super(CharacterTraitListView, self).get_context_data(**kwargs)
        context['character'] = Character.objects.get(pk = self.kwargs['characterpk'])
        return context

class TraitDetailView(LoginRequiredMixin, DetailView):
    model = Trait
    template_name = 'persomaker/trait_view.html'
    success_url = reverse_lazy('persomaker:charactertrait_list')

    def get_context_data(self, **kwargs):
        context = super(TraitDetailView, self).get_context_data(**kwargs)
        if 'pk' in self.kwargs:
            context['item'] = get_object_or_404(Trait, pk=self.kwargs['pk'])
        if 'characterpk' in self.kwargs:
            context['character'] = get_object_or_404(Character, pk=self.kwargs['characterpk'])
        try:
            instance = CharacterTrait.objects.get(character = get_object_or_404(Character, pk = self.kwargs['characterpk']),trait = get_object_or_404(Trait, pk = self.kwargs['pk']))
            form = CharacterTraitForm(instance = instance)
        except Exception as e:
            print(e)
            form = CharacterTraitForm(
            initial = { 'character' : get_object_or_404(Character, pk=self.kwargs['characterpk']),'trait':get_object_or_404(Trait, pk=self.kwargs['pk']),})
        context['form'] = form
        return context

    def post(self, request, *args,**kargs):
        self.object = self.get_object()
        try:
            instance = CharacterTrait.objects.get(character = get_object_or_404(Character, pk=self.kwargs['characterpk']),trait = get_object_or_404(Trait, pk=self.kwargs['pk']))
            form = CharacterTraitForm(self.request.POST, instance = instance)
        except Exception as e:
            print(e)
            form = CharacterTraitForm(self.request.POST,
            initial = { 'character' : get_object_or_404(Character, pk=self.kwargs['characterpk']),'trait':get_object_or_404(Trait, pk=self.kwargs['pk']),})
        if form.is_valid():
            form.save()
            return redirect('persomaker:charactertrait_list', self.kwargs['characterpk'])
        else:
            return self.render_to_response(context=self.get_context_data())

class CharacterTraitDelete(LoginRequiredMixin, DeleteView):
    model = CharacterTrait
    template_name = "persomaker/characterskill_delete.html"
    def get_success_url(self):
        character = self.object.character
        success_url = reverse('persomaker:trait_list', args=[character.id])
        return success_url

#///////////////////////////////////////////////////////////////////////////////
#URL related to Skill & CharacterSkill Models

class CharacterSkillListView(LoginRequiredMixin, ListView):
    model = CharacterSkill
    template_name = 'character/Character_list.html'
    def get_context_data(self, **kwargs):
        # Get queryset by category item
        context = super(CharacterSkillListView, self).get_context_data(**kwargs)
        categories = (
                            ('90','Academic knowledge'),
                            ('91','Interests knowledge'),
                            ('92','Professional knowledge'),
                            ('93','Street knowledge'),
                            ('96','Active skill'),
                            ('98','Language'),
                            ('99','Attribute'),
                            )
        category2 ={}
        for value in categories:
            item = {value[1] : CharacterSkill.objects.filter(skill__skillset_choice = value[0], character_id = self.kwargs['characterpk'])}
            category2.update(item)
        context['categories'] = category2
        if 'characterpk' in self.kwargs:
            context['character'] = get_object_or_404(Character, pk=self.kwargs['characterpk'])
        return context


class CharacterSkillDelete(LoginRequiredMixin, DeleteView):
    model = CharacterSkill
    def get_success_url(self):
        character = self.object.character
        return reverse('persomaker:skill_list', args=[character.id])

class CharacterSkillDetailView(LoginRequiredMixin, DetailView):
    model = CharacterSkill
    template_name = 'persomaker/characterskill_delete.html',
    success_url = reverse_lazy('persomaker:skill_list')
    def get_context_data(self,**kwargs):
        context = super(CharacterSkillDetailView, self).get_context_data(**kwargs)
        form = CharacterSkillModifyForm( instance = self.object)
        context['form'] = form
        return context
    def post(self, request, *args,**kargs):
        object = self.get_object()
        form = CharacterSkillModifyForm(self.request.POST)
        if form.is_valid():
            instance = form.save()
            return redirect('persomaker:skill_list', instance.character_id)
        else:
            return render(request, 'persomaker/characterskill_detail.html',
            {'form': form,})

class CreateCharacterSkillView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CharacterCreationForm
    template_name = 'persomaker/create_character.html'

    def get_success_url(self):
        return reverse('persomaker:module_list', args=[self.object.id,0])

    def get_form_kwargs(self):
        kwargs = super(CreateCharacterSkillView, self).get_form_kwargs()
        kwargs['player'] = self.request.user # pass the 'user' in kwargs
        return kwargs

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

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#deprecated views (To be deleted)
def action_effect(request,objectpk,actionpk):
    if request.method =="POST":
        instance = Character.objects.get(id=CharacterWeapon.objects.get(id=objectpk).character_id)
        current_object = CharacterWeapon.objects.get(id=objectpk)
        current_action = Action.objects.get(id=actionpk)
        #for modifier in current_action.modifier_effect.all()
        return redirect('persomaker:character_profile', instance.id)

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
