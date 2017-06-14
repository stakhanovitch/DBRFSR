from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Invitation, Circle
from django import forms


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class InvitationForm(ModelForm):
    class Meta:
        model = Invitation
        exclude = ('sender',)


class CircleForm(ModelForm):
    class Meta:
        model = Circle
        exclude = ('owner',)
