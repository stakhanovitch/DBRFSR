from django.forms import ModelForm
from personal_calendar.models import Evenement,Evenement_Participant

class EventForm(ModelForm):
    class Meta:
        model = Evenement
        exclude = ['participants']

class Evenement_ParticipantForm(ModelForm):
    class Meta:
        model = Evenement_Participant
        fields = '__all__'
