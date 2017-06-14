from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from ticket.models import Task
from django.template import Context, Template
# Create your views here.
def home(request,name=None):
    if name:
        test = ('lol',name)
    else:
        test =('lol')
    return HttpResponse(test)

def ticket_listing(request):
    format = "%Y-%m-%d"
    objects = Task.objects.all()
    if request.method == 'GET':
        if 'closed' in request.GET:
            if request.GET['closed'] =='true':
                objects = objects.filter(closed = True)
            else:
                objets = objects.filter(closed = False)
                if 'start' in request.GET and request.GET['start'] !='':
                    objets = objets.filter(due_date__gte=datetime.strptime(request.GET['start'], format))
                if 'end' in request.GET and request.GET['end'] !='':
                    objets = objets.filter(due_date__gte=datetime.strptime(request.GET['end'], format))
    context = Context(request)
    return render_to_response('ticket/list.html',{'objects' : objects},context)

def ticket_detail(request, id):
    objet = Task.objects.get(pk=id)
    return render_to_response('ticket/detail.html',{'objet':objet})
