from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from itertools import chain
from .models import Character,Skill,CharacterSkill
from django.urls import reverse
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'persomaker/index.html'
    context_object_name = 'latest_character_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Character.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Character
    template_name = 'persomaker/detail.html'


class ResultsView(generic.DetailView):
    model = Character
    template_name = 'persomaker/result.html'


def creation(request, pk):
    template = loader.get_template('persomaker/creation.html')
    character = get_object_or_404(Character, pk=pk)
    print(character)
    try:
        selected_choice = character.characterskill_set.get(pk=request.POST['charskill'])
    except (KeyError, Character.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'persomaker/creation.html', {
            'character': character,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.level += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        context = {'pk':pk}
        return HttpResponseRedirect(reverse('persomaker:result', args=(character.id,)))

def echec(request, pk):
    response = "echec %s."
    return HttpResponse(response % pk
    )

