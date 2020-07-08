from django.db import models

from django.contrib.auth.models import User
from rooms.models import Room



class Avatar(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='avatars')

    def __str__(self):
        return f'{self.name} Avatar'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True, default=1)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, editable=False)

    @property
    def display_username(self):
        return f'@{self.user.username}'

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        return f'{self.user.username} Profile'

