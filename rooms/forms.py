from django import forms
from django.core.exceptions import ValidationError

from .models import Room

class RoomJoinForm(forms.Form):
    code = forms.UUIDField(
        label="Enter the room code (ask the creator of the room)",
        error_messages={'invalid': 'Please enter a valid room code.'}
        )
