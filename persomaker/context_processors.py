from django.conf import settings
from persomaker.models import Character

def character(request):
    character = Character.objects.get(id = 18)
    return {'character':character}
