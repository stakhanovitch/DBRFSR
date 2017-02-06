from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django.template import loader
from itertools import chain
from .models import Character,Skill,Characterskill

def detail(request, character_id):
    personnaldata={'name':Character.objects.get(id=character_id).name,
                    'karma':Character.objects.get(id=character_id).karma,
                    'nuyen':Character.objects.get(id=character_id).nuyen,
                    }

    field_names = [u'skill_id',u'level',u'levelmax',]
    for i in Characterskill.objects.filter(skill__in=Skill.objects.filter(group='ATTRIBUTE')).values(*field_names):
        temp = {Skill.objects.get(id=i.get(u'skill_id')).name:{'level':i.get(u'level'),'levelmax':i.get(u'levelmax')}}
        personnaldata.update(temp)
    
    #for j in attribute:
    #    attribute_stat={'skill':j.objects.get("skill"),
    #                    'level':j.values_list("level"),
    #                    "levelmax":j.values_list("levelmax"),}
    #    attribute_list.append(attribute_stat)
    #print(attribute_list)
    
    #attribute_filter = Skill.objects.filter(group='ATTRIBUTE')
    #attribute_filter = attribute_filter.values_list("id",flat=True)
    #attribute = Characterskill.objects.values(skill_id = attribute_filter)
    #skills = 
    
    character_list = personnaldata
    print(character_list)
    template = loader.get_template('persomaker/index.html')
    context = character_list
    print "#"*10
    print(context)
    return HttpResponse(template.render(context, request))


def creation(request, character_id):
    template = loader.get_template('persomaker/creation.html')
    character = get_object_or_404(Character, pk=character_id)
    print(character)
    try:
        print('a')
        selected_choice = character.characterskill_set.get(pk=request.POST['characterskill_id'])
        if selected_choice:
            print ('test=' + str(selected_choice))
        else:
            print('vide')
    except (KeyError, Character.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'persomaker/creation.html', {
            'Character': Character,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.level += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        context = {'character_id':character_id}
        return HttpResponseRedirect(reverse('persomaker:creation', args=(character.id,)))

def results(request, character_id):
    response = "results %s."
    return HttpResponse(response % character_id)

def echec(request, character_id):
    response = "echec %s."
    return HttpResponse(response % character_id)
