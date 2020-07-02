from django.db import models

from django.contrib.auth.models import User
from rooms.models import Room

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, editable=False)
