from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from itertools import chain
from .models import Character,Skill,CharacterSkill,Module, ModuleSkill
from django.urls import reverse
from django.views import generic
from math import ceil
from .forms import CreationForm,ModuleForm,RealLifeForm,SkillSetForm, NewSkillSetForm
from django.forms import formset_factory,modelformset_factory
from functools import partial, wraps

class IndexView(generic.ListView):
    template_name = 'persomaker/index.html'
    context_object_name = 'character_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Character.objects.order_by('-name')[:50]

def creation(request, pk):
    template = loader.get_template('persomaker/creation.html')
    character = get_object_or_404(Character, pk=pk)
    #set de Skills/attributs
    attribute_set = character.characterskill_set.filter(skill__skillset_choice='99').order_by('skill__name')
    skill_set = character.characterskill_set.exclude(skill__skillset_choice='99').order_by('skill__name')
    personnal_data = {'name':character.name,} 
    #calcul finaux
    #final_calculation(character)
    context = {'pk':pk}
    return render(request, 'persomaker/creation.html', {
            'personnal_data':personnal_data,
            'character': character,
            'attribute_set':attribute_set,
            'skill_set':skill_set,
        })
   
    

def character_creation(request):
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
    def final_calculation(instance):
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
 
        

    instance = get_object_or_404(Character, pk=pk)
    SkillSetFormSet = modelformset_factory(CharacterSkill,fields=('skill','level','levelmax','character'), form = SkillSetForm, exclude=None, extra=0)
    
    qset = instance.characterskill_set.all()
    currentskillformset = SkillSetFormSet(queryset = qset)
    if request.method == 'POST':
        #deal with posting the data
        currentskillformset = SkillSetFormSet(request.POST)
        if currentskillformset.is_valid():
        #if it is not valid then the "errors" will fall through and be returned            
            currentskillformset.save()
            final_calculation(instance)
            instance.save()
        return redirect('persomaker:creation',
                        instance.id,               
        )
    return render(request, 'persomaker/character-skillset.html', {
        'currentskillformset':currentskillformset,
    })

    
def character_newskillset(request,pk):
    newskillformset = formset_factory(NewSkillSetForm)
    formset = newskillformset(form_kwargs={'instance': instance})
    instance = get_object_or_404(Character, pk=pk)
    return render(request, 'persomaker/character-skillset.html', {
        'newskillformset': formset,
    })

