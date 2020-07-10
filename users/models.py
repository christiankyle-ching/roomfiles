from django.db import models
from django.http import JsonResponse

from django.contrib.auth.models import User
from rooms.models import Room, Notification



class Avatar(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='avatars')

    def __str__(self):
        return f'{self.name} Avatar'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True, default=Avatar.objects.first().id)
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

    def get_notifications(self):
        user = self.user
        user_notifications = Notification.objects.filter(target=user)
        return user_notifications
        
    @property
    def notification_count(self):
        user = self.user
        notification_count = Notification.objects.filter(target=user, is_read=False).count()
        return notification_count
     