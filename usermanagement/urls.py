from django.conf.urls import include, url
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from persomaker.models import Character
from django.views.generic.list import ListView
from usermanagement.views import *
app_name = 'usermanagement'
urlpatterns = [


    url(r'^profile/player$', CharacterListView.as_view(model = Character,paginate_by=10), name='user_profile'),
    url(r'^profile/player/(?P<field>[\w-]+)/(?P<search>[\w-]+)$', CharacterListView.as_view(model = Character,paginate_by=10), name='user_profile'),
    url(r'^profile/game-master$', CircleList.as_view(), name='circle_list'),

    url(r'^circle/(?P<pk>[0-9]+)/$', CircleView.as_view(), name ='circle_view' ),
    url(r'^circle/create$', CircleCreateView.as_view(), name ='create_circle' ),
    url(r'^circle/add_player/(?P<pk>[0-9]+)$', CircleUpdateView.as_view(), name ='circle_update' ),
    url(r'^circle/delete/(?P<pk>[0-9]+)$', CircleDeleteView.as_view(), name ='delete_circle' ),

    url(r'^contact/all/$', ContactListView.as_view(), name='contact_list'),
    url(r'^contact/(?P<pk>[0-9]+)$', ContactView.as_view(), name ='contact_view'),

    url(r'^invitation/all/$', InvitationListView.as_view(template_name='user/invitation_list.html'), name = 'invitation_list'),
    url(r'^invitation/$', InvitationView.as_view(template_name='user/invitation_form.html'), name = 'create_invitation'),

    ]
