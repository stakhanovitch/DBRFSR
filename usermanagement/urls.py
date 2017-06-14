from django.conf.urls import include, url
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
from usermanagement.views import create_account
from django.contrib.auth.decorators import login_required
from persomaker.models import Character
from django.views.generic.list import ListView
from usermanagement.views import CharacterList, InvitationView, InvitationListView, CircleCreateView, CircleView, CircleList, UserInfoUpdateView, CircleUpdateView, CircleDeleteView
app_name = 'usermanagement'
urlpatterns = [
    url(r'^login/$', login, {'template_name':'user/login.html'}),
    url(r'^logout/$', logout, {'next_page': '/user/login/'}),
    url(r'^profile/player$', CharacterList.as_view(model = Character,paginate_by=10), name='user_profile'),
    url(r'^profile/player/(?P<field>[\w-]+)/(?P<search>[\w-]+)$', CharacterList.as_view(model = Character,paginate_by=10), name='user_profile'),
    url(r'^profile/game-master$', CircleList.as_view(), name='circle_list'),
    #url(r'^profile/$',login_required(profile,'user/profile.html'), name='user_profile'),
    url(r'^create_account', create_account),
    url(r'^succes', TemplateView.as_view(template_name='user/succes.html')),

    url(r'^invitation/all/$', InvitationListView.as_view(template_name='user/invitation_list.html'), name = 'invitation_list'),
    url(r'^invitation/$', InvitationView.as_view(template_name='user/invitation_form.html'), name = 'create_invitation'),

    url(r'^circle/(?P<pk>[0-9]+)/$', CircleView.as_view(), name ='circle_view' ),
    url(r'^circle/create$', CircleCreateView.as_view(), name ='create_circle' ),
    url(r'^circle/add_player/(?P<pk>[0-9]+)$', CircleUpdateView.as_view(), name ='circle_update' ),
    url(r'^circle/delete/(?P<pk>[0-9]+)$', CircleDeleteView.as_view(), name ='delete_circle' ),

    ]
