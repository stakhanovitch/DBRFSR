from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify

# Create your models here.

class Contact(models.Model):
    owner = models.ForeignKey(User)
    user = models.ForeignKey(User, related_name = 'friend')
    def __str__(self):
        return str(self.user)
    def all_contacts(self,user):
        return Contact.objects.filter(owner = user)
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
    image = models.ImageField(upload_to='circle', null=True)
    name = models.CharField(max_length = 250)
    slug = models.SlugField(blank=True,)
    description = models.TextField(null = True)
    owner = models.ForeignKey(User)
    circlecontacts = models.ManyToManyField(Contact)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Circle, self).save(*args, **kwargs)
    def __str__(self):
        return str(self.name)
    def characters(self):
        from persomaker.models import Character
        return Character.objects.filter(campaign = self)
    def pending_invitation(self):
        pass
    def pending_character(self):
        Contact.objects.filter(invitation_accepted !=True, owner = self.owner)
    def contacts (self):
        return self.circlecontacts.all()
    def all_circles(self, user):
        return Circle.objects.filter(owner = user)
    def is_in_circle (self, user):
        if user in Circle.contact_set.all():
            return True
        else:
            return False
    def get_absolute_url(self):
        return reverse ('usermanagement:circle_view', kwargs={'pk':self.pk})
