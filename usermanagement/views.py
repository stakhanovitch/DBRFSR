from django.shortcuts import render
from django.http import HttpResponseRedirect
from forms import UserCreateForm, InvitationForm, CircleForm
from persomaker.models import Character
from .models import *

from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.conf import settings
from django.utils.encoding import force_text

class LoginRequiredMixin(LoginRequiredMixin):
    """
    mixin overide to redirect to home page
    """
    def get_login_url(self):
        """
        Override this method to override the login_url attribute.
        """
        login_url = self.login_url or settings.LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                '{0} is missing the login_url attribute. Define {0}.login_url, settings.LOGIN_URL, or override '
                '{0}.get_login_url().'.format(self.__class__.__name__)
            )
        return force_text(login_url)


class HomePageView(LoginView):
    """
    website homepage with login capability
    """
    template_name = "public/home.html"
    def get(self, request):
        get = super(HomePageView, self).get(self, request)
        print('test',self.request.user.is_anonymous())
        if not self.request.user.is_anonymous():
            return redirect ("usermanagement:user_profile")
        else:
            return get

    """
        def get_context_data(self, **kwargs):
            context = super(HomePageView, self).get_context_data(**kwargs)
            context['latest_articles'] = Article.objects.all()[:5]
            return context
    """

def create_account(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect ("usermanagement:user_profile")
    else:
        form = UserCreateForm()
    return render(request,'user/create.html',{'form':form})

class CharacterListView(LoginRequiredMixin, ListView):
    """
     display the Player homepage with all the characters he created
    """
    def get_context_data(self, **kwargs):
        context = super(CharacterListView, self).get_context_data(**kwargs)
        try:
            context['campaign'] = Circle.objects.filter(circlecontacts__in = Contact.objects.filter(user = self.request.user))
        except Exception as e:
            print('error ',e)
        return context
    def get_queryset(self):
        object_list = Character.objects.filter(player = self.request.user.id)
        if "field" in self.kwargs:
            object_list = object_list.filter((self.kwargs['field'],self.kwargs['search']))
        return object_list

class InvitationListView(LoginRequiredMixin,ListView):
    model = Invitation
    def get_queryset(self):
        object_list = Invitation.objects.filter(sender = self.request.user)
        print(object_list)
        return object_list

class InvitationView(LoginRequiredMixin,CreateView):
    form_class = InvitationForm
    model = Invitation
    def get_context_data(self, **kwargs):
        context = super(InvitationView, self).get_context_data(**kwargs)
        context['invitations'] = Invitation.objects.filter(sender = self.request.user)
        print(context['invitations'])
        return context

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
        message = '{0} added you to its contacts'.format(invitation.sender.username)
        contact = Contact(owner = invitation.sender, user = user)
        contact.save()
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
                contact = Contact(owner = invitation.sender, user = instance)
                contact.save()
                invitation.delete()
        except Invitation.DoesNotExist:
            pass
post_save.connect(create_contact_on_user_create, sender = User)

class CircleList(LoginRequiredMixin,ListView):
    model = Circle
    template_name = 'user/circle_list.html'
    def get_queryset(self):
        object_list = Circle.objects.filter(owner = self.request.user)
        return object_list

class CircleView(LoginRequiredMixin,DetailView):
    model = Circle
    template_name = 'user/simple_display.html'

class CircleCreateView(LoginRequiredMixin, CreateView):
    form_class = CircleForm
    model = Circle
    template_name = 'user/simple_form.html'

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CircleCreateView, self).get_form_kwargs()
        kwargs['contacts'] = Contact.objects.filter(owner = self.request.user)
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit = False)
        obj.owner = self.request.user
        obj.save()
        return redirect('usermanagement:circle_list')

class CircleUpdateView(LoginRequiredMixin, UpdateView):
    model = Circle
    form_class = CircleForm
    template_name = 'user/simple_form.html'
    def get_form_kwargs(self, **kwargs):
        kwargs = super(CircleUpdateView, self).get_form_kwargs()
        kwargs['contacts'] = Contact.objects.filter(owner = self.request.user)
        return kwargs

    def get_success_url(self):
        return reverse('usermanagement:circle_list')

class CircleDeleteView(LoginRequiredMixin, DeleteView):
    model = Circle
    template_name = 'user/simple_delete.html'
    def get_success_url(self):
        return reverse('usermanagement:circle_list')

class UserInfoUpdateView(LoginRequiredMixin, UpdateView):
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

class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'user/contact_list.html'
    def get_queryset(self):
        object_list = Contact.objects.filter(owner = self.request.user)
        return object_list

class ContactView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'user/contact_view.html'

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        try:
            context['campaign'] = self.object.all_circle(self.request.user)
            print(context['campaign'])
        except Exception as e:
            print(e)
        return context
