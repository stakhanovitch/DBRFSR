import collections
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from itertools import chain
from .models import Character,Skill,CharacterSkill,Module, ModuleSkill
from django.urls import reverse
from django.views import generic
from math import ceil
from .forms import CreationForm,ModuleForm,RealLifeForm,SkillSetForm, NewSkillSetForm
from django.forms import formset_factory,modelformset_factory,inlineformset_factory
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
