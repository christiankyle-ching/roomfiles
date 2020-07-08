from django.contrib.auth.models import User
from .models import Profile, Avatar

from django.contrib.auth.forms import UserCreationForm 
from django import forms



class UserRegisterForm(UserCreationForm):
    username = forms.CharField(min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False, help_text='Optional. A valid email address will be used to reset password.')

    class Meta:
        model = User
        fields = ('email',)



class ProfileUpdateForm(forms.ModelForm):
    avatars = Avatar.objects.all()

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name')

