from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

# Create your models here.

class UserInfo(models.Model):
    notes = models.TextField()

class Player(models.Model):
    owner = models.ForeignKey(User)
    user = models.ForeignKey(User, related_name = 'friend')
    invitation_send = models.NullBooleanField()
    invitation_accepted = models.NullBooleanField()
    optional_information = models.OneToOneField(UserInfo, blank = True, null = True)
    def __str__(self):
        return str(self.owner)
    def all_contacts(self,user):
        return Player.objects.filter(owner = user)
    def all_circle(self,user):
        return Circle.objects.filter(owner = user)
    def get_absolute_url(self):
        return reverse('usermanagement:user_profile', kwargs={'pk':self.pk})

class Invitation(models.Model):
    email = models.EmailField()
    sender = models.ForeignKey(User)
    def __unicode__(self):
        return self.email
    def get_absolute_url(self):
        return reverse('usermanagement:invitation_list')
    class Meta:
        unique_together = ('email', 'sender')

class Circle(models.Model):
    name = models.CharField(max_length = 250)
    description = models.TextField(null = True)
    owner = models.ForeignKey(User)
    players = models.ManyToManyField(Player)
    def pending_invitation(self):
        pass
    def pending_character(self):
        Player.objects.filter(invitation_accepted !=True, owner = self.owner)
    def contacts (self):
        return self.user_info.contact_set.all()
    def all_circles(self, user):
        return Circle.objects.filter(owner = user)
    def is_in_circle (self, user):
        if user in Circle.player_set.all():
            return True
        else:
            return False
    def get_absolute_url(self):
        return reverse ('usermanagement:circle_view', kwargs={'pk':self.pk})
