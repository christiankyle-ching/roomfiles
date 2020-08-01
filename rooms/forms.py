from django import forms
from django.core.exceptions import ValidationError

from .models import Room

class RoomJoinForm(forms.Form):
    code = forms.UUIDField(
        label="Enter the room code (ask the creator of the room)",
        error_messages={'invalid': 'Please enter a valid room code.'}
        )

class ContactForm(forms.Form):
    CATEGORIES = [
        (0, "Suggestion / Request a Feature"),
        (1, "Question / Help"),
        (2, "Problem / Bugs"),
    ]
    subject = forms.CharField(min_length=10, error_messages={'min_length':'Please explain more.'})
    category = forms.ChoiceField(choices=CATEGORIES, required=True)
    message = forms.CharField(min_length=10, error_messages={'min_length':'Please explain more.'}, widget=forms.Textarea)

    def get_category_display(self, category_id):
        try:
            category_id = int(category_id)
            return self.CATEGORIES[category_id][1]
        except:
            return ''
        