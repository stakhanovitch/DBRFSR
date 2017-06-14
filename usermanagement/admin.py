from django.contrib import admin

from .models import Player, Circle, UserInfo, Invitation
# Register your models here.
admin.site.register(Player)
admin.site.register(Circle)
admin.site.register(UserInfo)
admin.site.register(Invitation)
