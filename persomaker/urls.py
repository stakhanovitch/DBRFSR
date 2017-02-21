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

from . import views

app_name = 'persomaker'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/creation/$', views.creation, name='creation'),
    url(r'^character-creation/$', views.character_creation, name='character_creation'),
    url(r'^(?P<pk>[0-9]+)/character-module/$', views.character_module, name='character_module'),
    url(r'^(?P<pk>[0-9]+)/character-skillset/$', views.character_skillset, name='character_skillset'),
    url(r'^(?P<pk>[0-9]+)/character-newskillset/$', views.character_newskillset, name='character_newskillset'),
]


