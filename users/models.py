from django.db import models
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from rooms.models import Room, Notification

def get_ann_contenttype():
    return ContentType.objects.get_by_natural_key('rooms', 'announcement')

def get_file_contenttype():
    return ContentType.objects.get_by_natural_key('rooms', 'file')

def get_default_avatar():
    return Avatar.objects.first().id

class Avatar(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='avatars')

    def __str__(self):
        return f'{self.name} Avatar'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)

    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, default=get_default_avatar())
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
        return self.get_unread_notifications.filter(
            action_obj_contenttype=get_file_contenttype()
        )

    @property
    def get_unread_files_id(self):
        qs = self.get_unread_notifications.filter(
            action_obj_contenttype=get_file_contenttype()
        ).values('action_obj_id')
        map_id = map( lambda pair : pair['action_obj_id'], qs )
        return list(map_id)

    @property
    def get_unread_announcements(self):
        return self.get_unread_notifications.filter(
            action_obj_contenttype=get_ann_contenttype()
        )
    
    @property
    def get_unread_announcements_id(self):
        qs = self.get_unread_notifications.filter(
            action_obj_contenttype=get_ann_contenttype()
        ).values('action_obj_id')
        map_id = map( lambda pair : pair['action_obj_id'], qs )
        return list(map_id)

    

    @property
    def notification_count(self):
        return self.get_unread_notifications.count()

    @property
    def notification_count_ann(self):
        return self.get_unread_announcements.count()

    @property
    def notification_count_file(self):
        return self.get_unread_files.count()



    # Methods
    def notifications_read_all(self):
        user = self.user
        user_notifications = Notification.objects.filter(target=user)

        for notif in user_notifications:
            notif.read()
    