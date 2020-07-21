from users.models import User
from .models import Profile, Avatar

from django.contrib.auth.forms import UserCreationForm 
from django import forms



class UserRegisterForm(UserCreationForm):
    username = forms.CharField(min_length=8)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileUpdateForm(forms.ModelForm):
    avatars = Avatar.objects.all()

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name')

