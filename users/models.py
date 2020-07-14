from django.db import models
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from rooms.models import Room, Notification

ANN_CONTENT_TYPE = ContentType.objects.get_by_natural_key('rooms', 'announcement')
FILE_CONTENT_TYPE = ContentType.objects.get_by_natural_key('rooms', 'file')


class Avatar(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='avatars')

    def __str__(self):
        return f'{self.name} Avatar'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, editable=False)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def display_username(self):
        return f'@{self.user.username}'

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'
    

    
    @property
    def get_unread_notifications(self):
        return Notification.objects.filter(
            target=self.user, 
            is_read=False,
        )

    @property
    def get_unread_files(self):
        return self.get_unread_notifications().filter(
            action_obj_contenttype=FILE_CONTENT_TYPE
        )
    
    @property
    def get_unread_announcements(self):
        return self.get_unread_notifications().filter(
            action_obj_contenttype=ANN_CONTENT_TYPE
        )

    

    @property
    def notification_count(self):
        return self.get_unread_notifications().count()

    @property
    def notification_count_ann(self):
        return self.get_unread_announcements().count()

    @property
    def notification_count_file(self):
        return self.get_unread_files().count()



    # Methods
    def notifications_read_all(self):
        user = self.user
        user_notifications = Notification.objects.filter(target=user)

        for notif in user_notifications:
            notif.read()
    