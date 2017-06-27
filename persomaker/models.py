# -*-coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from model_utils import FieldTracker
from django.conf import settings
from django.template.defaultfilters import slugify
from django.db import models
from usermanagement.models import Circle
from itertools import chain
from django.http import HttpResponseRedirect

class Module (models.Model):
    """
    A module is a bundle of several objects such as : Skills, option (self reference), qualities
    """
    name = models.CharField(max_length=70, default = None)
    description = models.TextField(max_length=5000, blank=True)
    image = models.ImageField(upload_to='module', null=True, blank=True)
    page = models.IntegerField(default=0, blank=True)
    rulebook = models.CharField(max_length=70, blank=True)
    METATYPE = '0'
    TALENT = '1'
    NATIONALITY = '2'
    FORMATIVE_YEARS = '3'
    TEEN_YEARS = '4'
    FURTHER_EDUCATION = '5'
    REAL_LIFE = '6'
    OPTION = '7'
    MODULE_CHOICE = ((METATYPE, 'Metatype'),
                     (NATIONALITY, 'Nationality'),
                     (FORMATIVE_YEARS, 'Formative years'),
                     (TEEN_YEARS, 'Teen years'),
                     (FURTHER_EDUCATION, 'Further education'),
                     (REAL_LIFE, 'Real life'),
                     (TALENT, 'Talent'),
                     (OPTION, 'Options'),

    )
    module_bundle = models.CharField(
        max_length=1,
        choices= MODULE_CHOICE,
        default='',
        )

    skills = models.ManyToManyField('Skill', through='ModuleSkill', related_name='skills')
    qualities = models.ManyToManyField('Quality', blank=True, default=None,)
    karma_cost = models.CharField(max_length=70, blank=True)
    options = models.ManyToManyField("self", blank=True)
    def __str__(self):
        return self.name

class Character(models.Model):
    """
    A character is the entry point of any RPG. the Character is link to skills and modules
    A character have RP infos : name, description, ethnicity, age, sex...
    Character object
    """
    ########### RP ###########
    image = models.ImageField(upload_to='character', null=True)
    name = models.CharField(max_length=70)
    # alias = models.CharField(max_length=70)
    description = models.CharField(max_length=2000, blank=True)
    ethnicity = models.CharField(max_length=70, blank=True)
    age = models.IntegerField(default=0)
    MALE = 'M'
    FEMALE = 'F'
    UNKNOWN = 'U'
    MODULE_CHOICE = ((MALE, 'Male'),
                  (FEMALE, 'Female'),
                  (UNKNOWN, 'Unknown'),
                  )
    sex = models.CharField(
        max_length=1,
        choices= MODULE_CHOICE,
        default=UNKNOWN,
        )

    ########### Stat ###########
    karma = models.IntegerField(default=0)
    nuyen = models.IntegerField(default=0)
    credibility = models.IntegerField(default=0)
    notoriety = models.IntegerField(default=0)
    awareness = models.IntegerField(default=0)

    ########### relation  ###########
    inventory = models.ManyToManyField('Obj', through='CharacterObj', related_name='inventory')
    skills = models.ManyToManyField('Skill', through='CharacterSkill', related_name='characters')
    modules = models.ManyToManyField('Module', through='CharacterModule', through_fields=('character','module'),related_name='modules')
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    campaign = models.ForeignKey('usermanagement.Circle', null=True, blank=True, default=None,)

    def __str__(self):
        return self.name
    def physical_condition(self):
        return range(CharacterSkill.objects.get(character = self, skill__name ='Physical condition').level)
    def get_absolute_url(self):
        return "/persomaker/character/profile/%s" % self.id


class CharacterModule(models.Model):
    character = models.ForeignKey(Character)
    module = models.ForeignKey(Module)
    charactermoduleoption = models.ForeignKey(Module, blank=True, default=None, null = True, related_name='charactermoduleoption')
    def __str__(self):
        return "%s, %s" % (self.character, self.module)
    class Meta:
        unique_together = ("character","module")

    def delete(self, *args, **kwargs):
        """
        lower the level of all the characterskill bound to the character by the module
        If the level = 0 -> delete the CharacterSkill
        """
        super(CharacterModule, self).delete(*args, **kwargs)
        #define the pool of ModuleSkill
        print('beginning of the process')
        try:
            moduleskill_set = self.module.moduleskill_set.all()
        except Exception as e:
            moduleskill_set = []
        #define the pool of ModuleSkill link to the module's option
        try:
            option_moduleskill_set = self.charactermoduleoption.moduleskill_set.all()
        except Exception as e:
            option_moduleskill_set = []
        #If the characterskill exist, we control if the characterskill have been upgraded in the skill step
        #if the character skill minus module skill level equal to 0, we delete the characterskill
        print('this is the chain :',moduleskill_set,"/",option_moduleskill_set)
        for tempmoduleskill in chain(moduleskill_set,option_moduleskill_set):
            print(tempmoduleskill)
            character_skill = CharacterSkill.objects.filter(skill = tempmoduleskill.skill , character = self.character).first()
            print(character_skill)
            if character_skill:
                #try:
                print('character_skill.level',character_skill.level)
                print('tempmoduleskill.level',tempmoduleskill.level)
                print('character_skill.levelmax',character_skill.levelmax)
                print('tempmoduleskill.levelmax',tempmoduleskill.levelmax)
                if (character_skill.level - tempmoduleskill.level) == 0 and (character_skill.levelmax - tempmoduleskill.levelmax) == 0:
                    character_skill.delete()
                else:

                    character_skill.level -=  tempmoduleskill.level
                    character_skill.levelmax -=  tempmoduleskill.levelmax
                    character_skill.save()
                #except Exception as e:
            #    pass
        #when we finish the process, we delete the CharacterModule
        print('finish')
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

class Skill(models.Model):
    name = models.CharField(max_length=70)
    slug = models.SlugField(blank=True,)
    abstract = models.CharField(max_length=5000, blank=True, null = True)
    description = models.CharField(max_length=5000, blank=True, null = True)
    page = models.IntegerField(default=0, blank=True, null = True)
    rulebook = models.CharField(max_length=70, blank=True, null = True)
    ACADEMIC_KNOWLEDGE = '90'
    INTERESTS_KNOWLEDGE = '91'
    PROFESSIONAL_KNOWLEDGE = '92'
    STREET_KNOWLEDGE = '93'
    CALCULATED = '94'
    GROUPSKILL = '95'
    ACTIVE = '96'

    LANGUAGE = '98'
    ATTRIBUTE = '99'
    SKILLSET_CHOICE = (
                       (CALCULATED,'Calculated'),
                       (GROUPSKILL,'Groupskill'),
                       (ACTIVE,'Active skill'),
                       (LANGUAGE,'Language'),
                       (ATTRIBUTE,'Attribute'),
                       (ACADEMIC_KNOWLEDGE,'Academic knowledge'),
                       (INTERESTS_KNOWLEDGE,'Interests knowledge'),
                       (PROFESSIONAL_KNOWLEDGE,'Professional knowledge'),
                       (STREET_KNOWLEDGE,'Street knowledge'),

    )
    skillset_choice = models.CharField(
        max_length=2,
        choices = SKILLSET_CHOICE,
        default='',
        blank=True,
        null=True,
        )
    context = models.CharField(max_length=500, blank=True, null = True)
    default = models.NullBooleanField(blank=True, null=True, default=None,)
    ########### relation  ###########
    attribute = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='%(class)s_attribute')
    limit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='%(class)s_limit')
    skillgroup = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None, related_name='%(class)s_skillgroup')
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Skill, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return "/skill/%s" % self.id
    def delete_url(self):
        return "/skill/delete/%s/" %self.id

class SkillSpecialisation(models.Model):
    name = models.CharField(max_length=70)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True, blank=True, default=None,)
    def __str__(self):
        return self.name

class CharacterSkill(models.Model):
    #name = models.CharField(max_length=70, default = None)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    levelmax = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    karma_cost = models.IntegerField(default=0)
    tracker = FieldTracker()
    specialisations = models.ManyToManyField(SkillSpecialisation, blank=True, default=None,)

    def __str__(self):
        return "%s, %s" % (self.character, self.skill)

    class Meta:
        unique_together = ("character","skill")

    def delete_url(self):
        return "/persomaker/skill/delete/%s" %self.id

    def dice_pool(self):
        attribute = CharacterSkill.objects.get(skill = self.skill.attribute, character = self.character)
        dice_pool = self.level + attribute.level
        return dice_pool

    def modifier_pool(self):
        attribute = CharacterSkill.objects.get(skill = charskill.skill.attribute, character = self.character)
        skill_modifier_pool = sum(Modifier.objects.filter(skill = self).values_list('value',flat=True))
        attribute_modifier_pool = sum(Modifier.objects.filter(skill = attribute).values_list('value',flat=True))
        modifier_pool = attribute_modifier_pool + skill_modifier_pool
        return modifier_pool

class ModuleSkill (models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    levelmax = models.IntegerField(default=0)
    specialisations = models.ManyToManyField(SkillSpecialisation, blank=True, default=None,)
    #order = models.IntegerField(default=0)
    def __str__(self):
        return "%s, %s" % (self.module, self.skill)

######################################
#       en construction              #
######################################

class Action(models.Model):
    name = models.CharField(max_length=70, default = None)
    FREE = '01'
    SIMPLE = '02'
    COMPLEX = '03'
    VARIABLE = '04'
    INTERRUPT = '05'
    ACTION_TYPE = ((FREE, 'Free action'),
                    (SIMPLE, 'Simple action'),
                    (COMPLEX, 'Complex action'),
                    (VARIABLE, 'Variable action'),
                    (INTERRUPT, 'Interruption'),)
    action_type = models.CharField(
        max_length=2,
        choices = ACTION_TYPE,
        default='',
        blank=True,
        null=True,
        )
    def __str__(self):
        return self.name

class Obj(models.Model):
    """docstring for ."""
    name = models.CharField(max_length=70, default = None)
    description = models.CharField(max_length=5000, blank=True)
    authorized_actions = models.ManyToManyField(Action)
    skill_category = models.ForeignKey(Skill, on_delete=models.CASCADE, null = True)
    WEAPON = '01'
    ARMOR = '02'
    COMMLINK = '03'
    OBJECT_CATEGORY = (
                    (WEAPON, 'Weapon'),
                    (ARMOR, 'Armor'),
                    (COMMLINK,'Commlink')
                )
    category = models.CharField(
        max_length=2,
        choices = OBJECT_CATEGORY,
        default='',
        blank=True,
        null=True,
        )
    stats = models.ManyToManyField('Stat', through='ObjStat', related_name='stats')
    def __str__(self):
        return self.name

class CharacterObj(models.Model):
    """docstring for ."""
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    obj = models.ForeignKey(Obj, on_delete=models.CASCADE)
    is_equiped = models.BooleanField(default = False)
    def __str__(self):
        return "%s, %s (%s)" % (self.obj, self.character, self.id)
    def dice_pool(self):
        charskill = CharacterSkill.objects.get(skill = self.obj.skill_category, character = self.character)
        attribute = CharacterSkill.objects.get(skill = charskill.skill.attribute, character = self.character)
        dice_pool = charskill.level + attribute.level
        return dice_pool

    def modifier_pool(self):
        charskill = CharacterSkill.objects.get(skill = self.obj.skill_category, character = self.character)
        attribute = CharacterSkill.objects.get(skill = charskill.skill.attribute, character = self.character)
        skill_modifier_pool = sum(Modifier.objects.filter(impacted_skill = charskill.skill, impacted_object=self).values_list('value',flat=True))
        attribute_modifier_pool = sum(Modifier.objects.filter(impacted_skill = attribute.skill, impacted_object=self).values_list('value',flat=True))
        modifier_pool = attribute_modifier_pool + skill_modifier_pool
        return modifier_pool

class Stat(models.Model):
    """docstring for ."""
    name = models.CharField(max_length=70, default = None)
    description = models.CharField(max_length=5000, blank=True)
    def __str__(self):
        return self.name

class ObjStat(models.Model):
    """docstring for ."""
    stat = models.ForeignKey(Stat, on_delete=models.CASCADE)
    obj = models.ForeignKey(Obj, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)
    def __str__(self):
        return "%s, %s (%s)" % (self.obj, self.stat, self.value)


class ActionEffect(models.Model):
    name = models.CharField(max_length=70, default = None)
    parent_action = models.ManyToManyField(Action)
    value = models.IntegerField(default=0)
    impacted_object = models.CharField(max_length=70, default = None)
    impacted_field = models.CharField(max_length=70, default = None)

class Quality(models.Model):
    name = models.CharField(max_length=70, default = None)
    karma_cost = models.IntegerField(default=0)
    QUALITY = '01'
    DEFAULT = '02'
    QUALITY_TYPE = ((QUALITY, 'Quality'),
                    (DEFAULT, 'Default'),
                )
    quality_type = models.CharField(
        max_length=2,
        choices = QUALITY_TYPE,
        default='',
        blank=True,
        null=True,
        )
    page = models.IntegerField(default=0, blank=True)
    rulebook = models.CharField(max_length=70, blank=True)
    description = models.CharField(max_length=5000, blank=True, null = True)
    character = models.ManyToManyField(Character,default = None, blank=True,)
    def __str__(self):
        return self.name

class Modifier(models.Model):
    name = models.CharField(max_length=70, default = None)
    impacted_skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    character = models.ManyToManyField(Character,default = None, blank=True,)
    impacted_object = models.ManyToManyField(CharacterObj, default = None, blank=True,)
    value = models.IntegerField(default=0)
    def __str__(self):
        return self.name
