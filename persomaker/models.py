from __future__ import unicode_literals
from django.db import models


class Character(models.Model):
    ########### RP ###########
    #picture = models.ImageField(null=True)
    name = models.CharField(max_length=70)
    # alias = models.CharField(max_length=70)
    description = models.CharField(max_length=2000)
    ethnicity = models.CharField(max_length=70)
    age = models.IntegerField(default=0)
    MALE = 'M'
    FEMALE = 'F'
    UNKNOWN = 'U'
    SEX_CHOICE = ((MALE, 'Male'),
                  (FEMALE, 'Female'),
                  (UNKNOWN, 'Unknown'),
                  )
    sex = models.CharField(
        max_length=1,
        choices= SEX_CHOICE,
        default=UNKNOWN,
        )
        
    ########### Stat ###########
    karma = models.IntegerField(default=0)
    nuyen = models.IntegerField(default=0)
    credibility = models.IntegerField(default=0)
    notoriety = models.IntegerField(default=0)
    awareness = models.IntegerField(default=0)

    ########### Skills  ###########
    skills = models.ManyToManyField('Skill', through='CharacterSkill', related_name='characters')

    ###########  calculated skills  ###########
    initiative_physical = models.IntegerField(default=0)
    initiative_ar = models.IntegerField(default=0)    
    initiative_coldsim = models.IntegerField(default=0)
    initiative_hotsim = models.IntegerField(default=0)
    initiative_physical = models.IntegerField(default=0)
    initiative_astral = models.IntegerField(default=0)
    
    limit_mental = models.IntegerField(default=0)
    limit_physical = models.IntegerField(default=0)
    limit_social = models.IntegerField(default=0)

    condition_physical = models.IntegerField(default=0)
    condition_stun = models.IntegerField(default=0)
    condition_overflow = models.IntegerField(default=0)
    
    living_personna_attack = models.IntegerField(default=0)
    living_personna_dataprocessing = models.IntegerField(default=0)
    living_personna_devicerating = models.IntegerField(default=0)
    living_personna_firewall = models.IntegerField(default=0)
    living_personna_sleeze = models.IntegerField(default=0)

    attribute_skill_composure = models.IntegerField(default=0)
    attribute_skill_judgeintention = models.IntegerField(default=0)
    attribute_skill_lifting = models.IntegerField(default=0)
    attribute_skill_memory = models.IntegerField(default=0)

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
    #attribute = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None)
    def __str__(self):
        return self.name


class CharacterSkill(models.Model):
    #name = models.CharField(max_length=70, default = None)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    levelmax = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    def __str__(self):
        return "%s, %s" % (self.character, self.skill)

class Module (models.Model):
    name = models.CharField(max_length=70, default = None)
    description = models.CharField(max_length=500, blank=True)
    page = models.IntegerField(default=0, blank=True)
    rulebook = models.CharField(max_length=70, blank=True)
    group = models.CharField(max_length=70, blank=True)
    skills = models.ManyToManyField('Skill', through='ModuleSkill', related_name='skills')
    karma_cost = models.CharField(max_length=70, blank=True)
    def __str__(self):
        return self.name
    
class ModuleSkill (models.Model):    
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    levelmax = models.IntegerField(default=0)
    #order = models.IntegerField(default=0)
    def __str__(self):
        return "%s, %s" % (self.module, self.skill)
    
    
######################################
#       en construction              #
######################################

class Quality(models.Model):
    pass
    
class Tag (models.Model):
    #ForeignKey(Characterskill
    pass

class Action (models.Model):
    pass
