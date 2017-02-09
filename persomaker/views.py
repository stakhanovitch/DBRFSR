from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from itertools import chain
from .models import Character,Skill,CharacterSkill,Module, ModuleSkill
from django.urls import reverse
from django.views import generic
from math import ceil
from .forms import CreationForm

class IndexView(generic.ListView):
    template_name = 'persomaker/index.html'
    context_object_name = 'character_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Character.objects.order_by('-name')[:5]


class DetailView(generic.DetailView):
    model = Character
    template_name = 'persomaker/detail.html'


class ResultsView(generic.DetailView):
    model = Character
    template_name = 'persomaker/result.html'


def creation(request, pk):
    def final_calculation(character):
        character.initiative_physical = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Intuition').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Reaction').id).level)
        character.initiative_ar = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Intuition').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Reaction').id).level)
        #Character.initiative_coldsim =  
        #Character.initiative_hotsim = 
        character.initiative_astral = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Intuition').id).level)*2

        character.limit_mental = ceil((int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Logic').id).level)*2+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Intuition').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Willpower').id).level))/3)
        character.limit_physical = ceil((int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Strength').id).level)*2+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Body').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Reaction').id).level))/3) 
        character.limit_social =ceil((int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Charisma').id).level)*2+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Willpower').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Essence').id).level))/3) 

        character.condition_physical = ceil(int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Body').id).level)/2)+8
        character.condition_stun = ceil(int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Willpower').id).level)/2)+8
        character.condition_overflow = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Body').id).level)

        character.living_personna_attack = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Charisma').id).level) 
        character.living_personna_dataprocessing = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Logic').id).level) 
        character.living_personna_devicerating = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Resonance').id).level) 
        character.living_personna_firewall = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Willpower').id).level) 
        character.living_personna_sleeze = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Intuition').id).level)
        character.attribute_skill_composure = int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Charisma').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Willpower').id).level)
        character.attribute_skill_judgeintention =  int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Charisma').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Intuition').id).level)
        character.attribute_skill_lifting =  int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Body').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Strength').id).level)
        character.attribute_skill_memory =  int(character.characterskill_set.get(skill_id=Skill.objects.get(name='Logic').id).level)+(character.characterskill_set.get(skill_id=Skill.objects.get(name='Willpower').id).level)

        

    template = loader.get_template('persomaker/creation.html')
    character = get_object_or_404(Character, pk=pk)
    #Faire un filtre qui distingue les skills des attributs
    attribute_filter = Skill.objects.filter(group='ATTRIBUTE')
    #set de Skills/attributs
    attribute_set = character.characterskill_set.filter(skill__in=attribute_filter)
    skill_set = character.characterskill_set.exclude(skill__in=attribute_filter)
    #calcul finaux
    final_calculation(character)


    try:
        selected_choice = character.characterskill_set.get(pk=request.POST['charskill'])
    except (KeyError, Character.DoesNotExist):
        # Redisplay the question voting form.
        
        return render(request, 'persomaker/creation.html', {
            'character': character,
            'attribute_set':attribute_set,
            'skill_set':skill_set,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.level += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        context = {'pk':pk}
        return HttpResponseRedirect(reverse('persomaker:creation', args=(character.id,)))

def echec(request, pk):
    response = "echec %s."
    return HttpResponse(response % pk
    )

def character_creation(request):
    
    def module_assign(pk,modulepk):
        print('metatype = human')
        characterobject = Character.objects.get(id=pk)
        moduleobject = Module.objects.get(id=1)
        print('test')
        test = moduleobject.moduleskill_set.all() 
        print(test)
        for tempmoduleskill in moduleobject.moduleskill_set.all():
            print(tempmoduleskill.skill_id)
            skillobject = get_object_or_404(Skill, pk = tempmoduleskill.skill_id )
            tempcharacterskill = characterobject.characterskill_set.create(
                character = characterobject,
                skill = skillobject,
                level = tempmoduleskill.level,
                levelmax = tempmoduleskill.levelmax,
                )

    form = CreationForm(request.POST)
    if form.is_valid():
        character = form.save(commit=False)
        character.save()
        charpk = character.id
        print ('character')
        print (character)
        module_assign(charpk,1)
        

        return redirect('persomaker:creation', pk=character.pk)
    else:
        form = CreationForm()
    
    return render(request, 'persomaker/character-creation.html', {'form': form})
    
