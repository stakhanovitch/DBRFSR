from __future__ import unicode_literals
from django.db import models

class Character(models.Model):
    #picture
    name = models.CharField(max_length=70)
    #alias = models.CharField(max_length=70)
    description = models.CharField(max_length=200)
    ethnicity = models.CharField(max_length=70)
    karma = models.IntegerField(default=0)
    nuyen = models.IntegerField(default=0)
    #skills = models.ManyToManyField(Skill)
    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=70)
    abstract = models.CharField(max_length=70, blank=True)
    description = models.CharField(max_length=500, blank=True)
    page = models.IntegerField(default=0, blank=True)
    rulebook = models.CharField(max_length=70, blank=True)
    group = models.CharField(max_length=70, blank=True)
    context = models.CharField(max_length=70, blank=True)
    default = models.NullBooleanField(blank=True, null=True, default=None,)
    attribute = models.ForeignKey('self', on_delete=models.CASCADE, null=True )
    def __str__(self):
        return self.name
    
class Characterskill(models.Model):
    #name = models.CharField(max_length=70, default = None)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True)
    level = models.IntegerField(default=0)
    levelmax = models.IntegerField(default=0)
    def __str__(self):
        return "%s, %s" % (self.character, self.skill)
    
######################################
# remettre les objets du tutoriels   #
######################################