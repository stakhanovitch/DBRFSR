from django.shortcuts import render, HttpResponseRedirect
from personal_calendar.models import Evenement, Evenement_Participant
from personal_calendar.forms import EventForm,Evenement_ParticipantForm
from django.forms import HiddenInput
from django.contrib.auth.models import User

def create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            return HttpResponseRedirect('/calendar/details/%i'%event.pk)
    else:
        form = EventForm()
    return render(request,'agenda/create.html',{'form':form})

def details(request,id):
    print(request.is_ajax())
    event = Evenement.objects.get(pk = id)
    if request.method == "POST":
        form = Evenement_ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/calendar/details/%i' %event.pk)
    else:
        form = Evenement_ParticipantForm(initial = {'evenement':event})
        participants = [user.pk for user in event.participants.all()]
        form.fields['participant'].queryset = User.objects.exclude(pk__in = participants)
        form.fields['evenement'].widget = HiddenInput()

    return render(request,'agenda/details.html',{
    'event':event,
    'form':form,
    })
def delete_participant(request, id, participant):
    if request.method == "POST":
        evenement = Evenement.objects.get(pk=id)
        participant = User.objects.get(pk = participant)
        a_supprimer = Evenement_Participant.objects.get(evenement = evenement, participant = participant)
        a_supprimer.delete()
    return HttpResponseRedirect('/calendar/details/%i' %evenement.id)

def liste(request):
    events = Evenement.objects.all()
    return render(request,'agenda/liste.html',{"events":events,})

def delete(request,id):
    if request.method =="POST":
        evenement = Evenement.objects.get(pk=id)
        evenement.delete()
    return HttpResponseRedirect('calendar/liste/')
    
def update(request, id):
    event = Evenement.objects.get(pk = id)
    if request.method =="POST":
        print request.POST
        form = EventForm(request.POST, instance = event)
        if form.is_valid():
            prout = form.save()
            return HttpResponseRedirect('agenda/details/%i'%prout.pk)
    else:
        form = EventForm()
    return render(request,'agenda/create.html',{'form':form})
