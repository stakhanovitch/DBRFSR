# -*-coding:utf-8 -*-
"""shadowrun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from persomaker.models import Obj,Skill,CharacterSkill
from django.views.generic.list import ListView
from persomaker.views import *
from django.urls import reverse_lazy
from . import views

app_name = 'persomaker'
urlpatterns = [
    url(r'^create/$', CreateCharacterView.as_view(), name='create_character'),
    url(r'^create/(?P<campaign_slug>[\w-]+)$', CreateCharacterView.as_view(), name='create_character'),
    url(r'^(?P<characterpk>[0-9]+)/module/list/$', ModuleListView.as_view(), name='module_list'),
    #url(r'^(?P<characterpk>[0-9]+)/module/list/(?P<categoriepk>[0-9]+)$', ModuleListView.as_view(), name='module_list'),
    url(r'^(?P<characterpk>[0-9]+)/module/(?P<pk>[0-9]+)$', ModuleView.as_view(), name='module_view'),
    url(r'^module/delete/(?P<pk>[0-9]+)$', CharacterModuleDelete.as_view(), name='module_delete'),
    url(r'^(?P<characterpk>[0-9]+)/skill/list$', CharacterSkillListView.as_view(), name='skill_list'),
    url(r'^(?P<characterpk>[0-9]+)skill/detail/$', CharacterSkillDetailView.as_view(), name='skill_detail'),

    #Charactermodulelist
    #url(r'^(?P<pk>[0-9]+)/character-module/$', CharacterSkillDetailView.as_view(), name='character_module'),
    #///////////////////////////////
    #url(r'^charactermodule/(?P<modulepk>[0-9]+)/(?P<pk>[0-9]+)$', CharacterModuleListView.as_view(), name='charactermodule_list'),
    #url(r'^skill/(?P<pk>[0-9]+)$', views.skill_view, name='skill'),
    #url(r'^skill/list/(?P<pk>[0-9]+)$', views.skill_list, name='skill_list'),

    url(r'^skill/add/(?P<pk>[0-9]+)/(?P<skillfilter>[0-9]+)$', views.skill_add, name='skill_add'),
    url(r'^skill/update/(?P<skillpk>[0-9]+)/(?P<instancepk>[0-9]+)$', views.skill_update, name='skill_update'),
    url(r'^skill/delete/(?P<pk>[0-9]+)$', CharacterSkillDelete.as_view(), name='skill_delete'),
    url(r'^skill/final_calculation/(?P<pk>[0-9]+)$', views.skill_final_calculation, name='final_calculation'),
    url(r'^character/profile/(?P<pk>[0-9]+)$', views.character_profile, name='character_profile'),
    url(r'^character/inventory/(?P<charpk>[0-9]+)$', views.character_inventory, name='character_inventory'),

    url(r'^action/effect/(?P<objectpk>[0-9]+)/(?P<actionpk>[0-9]+)$', views.action_effect, name='action_effect'),

    url(r'^object/view/(?P<id>[0-9]+)/$', views.object_view, name='object_view'),
    url(r'^object/list/(?P<id>[0-9]+)/$', views.object_list, name='object_list'),
    url(r'^object/list2/$', ListView.as_view(model = Obj,), name='object_list'),
    url(r'^object/buy/(?P<objpk>[0-9]+)/(?P<charpk>[0-9]+)/$', views.object_buy, name='object_buy'),
    url(r'^object/sell/(?P<objpk>[0-9]+)/(?P<charpk>[0-9]+)/$', views.object_sell, name='object_sell'),
    url(r'^object/equip/(?P<objpk>[0-9]+)/(?P<charpk>[0-9]+)/$', views.object_equip, name='equip'),
    #url(r'^(?P<pk>[0-9]+)/creation/$', views.creation, name='creation'),
    #url(r'^character-creation/$', views.character_creation, name='character_creation'),
    #url(r'^(?P<pk>[0-9]+)/character-skillset/$', views.character_skillset, name='character_skillset'),
    #url(r'^(?P<pk>[0-9]+)/character-newskillset/$', views.character_newskillset, name='character_newskillset'),
]
