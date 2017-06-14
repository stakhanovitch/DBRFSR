from django.shortcuts import render
from django.http import HttpResponseRedirect
from forms import UserCreateForm, InvitationForm, CircleForm
from persomaker.models import Character
from .models import Player, Invitation, Circle

from django.contrib.auth.models import User
from django.views.generic.detail import DetailView

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse



def create_account(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/user/profile/')
    else:
        form = UserCreateForm()
    return render(request,'user/create.html',{'form':form})

class CharacterList(ListView):
    """
     display the Player homepage with all the characters he created
    """
    def get_queryset(self):
        object_list = Character.objects.filter(player = self.request.user.id)
        if "field" in self.kwargs:
            object_list = object_list.filter((self.kwargs['field'],self.kwargs['search']))
        return object_list

class InvitationListView(ListView):
    model = Invitation
    def get_queryset(self):
        object_list = Invitation.objects.filter(sender = self.request.user)
        return object_list

class InvitationView(CreateView):
    form_class = InvitationForm
    model = Invitation
    def form_valid(self, form):
        obj = form.save(commit = False)
        obj.sender = self.request.user
        print(obj.sender)
        try:
            Invitation.objects.get(email=obj.email, sender=obj.sender)
            form.add_error('email',[u"An invitation has already been sent to this email address"])
            return super(InvitationView, self).form_invalid(form)
        except Invitation.DoesNotExist:
            pass
        obj.save()
        send_invitation(obj)
        return HttpResponseRedirect(obj.get_absolute_url())

def send_invitation(invitation):
    try:
        user = User.objects.get(email = invitation.email)
        message = '{0} added you to its Player'.format(invitation.sender.username)
        player = Player(owner = invitation.sender, user = user)
        player.save()
        invitation.delete()
        #Ajouter la liste des PJ d'une campagne
    except User.DoesNotExist:
        message = """
        {0} invited you to join its contacts.
        Sign_in on {1}user/create_account/ to accept the invitation
        """.format(invitation.sender.username, Site.objects.get_current().domain)
    send_mail(
            'An invitation has been sent',
            message,
            invitation.sender,
            [invitation.email],
            fail_silently = False,
            )

def create_contact_on_user_create(sender, instance, created, **kwargs):
    if created == True:
        try:
            invitations = Invitation.objects.filter(email = instance.email)
            for invitation in invitations:
                player = Player(owner = invitation.sender, user = instance)
                player.save()
                invitation.delete()
        except Invitation.DoesNotExist:
            pass
post_save.connect(create_contact_on_user_create, sender = User)

class CircleList(ListView):
    model = Circle
    template_name = 'user/circle_list.html'
    def get_queryset(self):
        object_list = Circle.objects.filter(owner = self.request.user)
        return object_list

class CircleView(DetailView):
    model = Circle
    template_name = 'user/simple_display.html'


class CircleCreateView(CreateView):
    form_class = CircleForm
    model = CircleForm
    template_name = 'user/simple_form.html'
    def form_valid(self, form):
        obj = form.save(commit = False)
        obj.owner = self.request.user
        obj.save()
        return redirect('usermanagement:circle_list')

class CircleUpdateView(UpdateView):
    model = Circle
    fields = ['players']
    template_name = 'user/simple_form.html'
    """
    #Do not work, to be refactored
    def get_form(self, form_class):
        form = super(CircleUpdateView, self).get_form(form_class)

        #form.fields['players'] = Player.objects.filter(owner = self.request.user)
        return form
    """
class CircleDeleteView(DeleteView):
    model = Circle
    template_name = 'user/simple_delete.html'
    def get_success_url(self):
        return reverse('usermanagement:circle_list')

class UserInfoUpdateView(UpdateView):
    def get_form(self, form_class):
        form = super(InfoUpdateView, self).get_form(form_class)
        form.fields['circle'] = Circle.objects.filter(owner = self.request.user)
        return form

    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kargs)
        if self.optional_information == None:
            infos = UserInfo.objects.create()
            self.optional_information = infos
            self.save()
            infos.save()

    def delete(self, *args, **kwargs):
        optional_information = self.optional_information
        super(Contact, self).delete(*args,**kwargs)
        optional_information.delete()
