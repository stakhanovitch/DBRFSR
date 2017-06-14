#-*-coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.db import models

class Evenement(models.Model):
    nom = models.CharField(max_length=250, unique=True)
    description = models.TextField()
    participants = models.ManyToManyField(
                       User,
                       through="Evenement_Participant",
                  )
    date = models.DateTimeField()
    lieu = models.TextField()
    def get_absolute_url(self):
        return "/calendar/details/%s" % self.id
    def delete_url(self):
        return "/agenda/delete/%s/" %self.id

class Evenement_Participant(models.Model):
    #notre table de relation
    evenement = models.ForeignKey(Evenement)
    participant = models.ForeignKey(User)
    status_choices = (
                      (0, "hôte"),
                      (1, "invité"),
                      (2, "désisté")
                      )
    status = models.IntegerField(choices=status_choices)

    def delete_url(self):
        return "/agenda/%i/participant/%i/delete/" % (self.evenement.id,
                                                      self.participant.id)


    class Meta:
        unique_together = ("evenement","participant")
