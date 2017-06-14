from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^create/$', views.create, name='create'),
    url(r'^details/(\d+)/$', views.details, name='details'),
    url(r'^(\d+)/participant/(\d+)/delete/$', views.delete_participant, name='delete_participant'),
    url(r'^liste/$', views.liste, name='liste'),
    url(r'^delete/(\d+)/$', views.delete, name='delete'),
    url(r'^update/(\d+)/$', views.update, name='update'),
    ]
