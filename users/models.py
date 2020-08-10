from django.db import models
from django.db.models import Q
from django.http import JsonResponse

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings

from django.contrib.contenttypes.models import ContentType
from rooms.contenttypes import get_ann_contenttype, get_file_contenttype



class ActiveUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    objects = UserManager()
    active = ActiveUserManager()

    def close_account(self):
        self.is_active = False
        self.save()

    class Meta:
        ordering = ['username']




class Avatar(models.Model):
    class Meta:
        ordering = ['name']
    
    name = models.CharField(max_length=30)
    image_url = models.URLField()

    def __str__(self):
        return f'{self.name} Avatar'




class ActiveProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__is_active=True)

class Profile(models.Model):

    class Meta:
        ordering = ['user__username']

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)

    avatar = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    user_rooms = models.ManyToManyField('rooms.Room', related_name="user_rooms", blank=True)

    objects = ActiveProfileManager()

    def __str__(self):
        return f'{self.user.username} Profile'


    @property
    def display_username(self):
        return f'@{self.user.username}'

    @property
    def display_name(self):
        if self.first_name == '' and self.last_name == '': return 'Unnamed'
        return f'{self.first_name} {self.last_name}'
    

    # Notifications
    def get_unread_notifications(self):
        return Notification.objects.filter(
            target=self.user, 
            is_read=False,
        )

    @property
    def notification_count(self):
        return self.get_unread_notifications().count()

    def get_notification_count_in_room(self, room):
        unread_notifs = self.get_notifications_in_room(room)
        return unread_notifs.count()

    def get_notifications_in_room(self, room):
        unread_notifs = Notification.objects.filter(
            Q(file__room=room) | Q(announcement__room=room),
            is_read=False, target=self.user,
            content_type__in=[get_ann_contenttype(), get_file_contenttype()],
            )
        
        return unread_notifs

    def get_unread_files(self, room):
        unread_notifs = self.get_notifications_in_room(room)
        unread_files = unread_notifs.filter(content_type=get_file_contenttype())

        return unread_files
    
    def get_unread_anns(self, room):
        unread_notifs = self.get_notifications_in_room(room)
        unread_anns = unread_notifs.filter(content_type=get_ann_contenttype())
        return unread_anns

    # Read all notification of specific contenttype (announcement or file)
    def notifications_read_objects_of_type(self, room, model_type):
        user = self.user
        content_type = ContentType.objects.get_by_natural_key('rooms', model_type)

        content_notifs = self.get_notifications_in_room(room).filter(content_type=content_type)

        for notif in content_notifs:
            notif.read()
        
        response = {
            'done' : True,
            'unseen_object' : 0,
            'unseen_total' : self.notification_count
            }
        
        return response

    # Read all notification
    def notifications_read_all(self):
        user = self.user
        notifications = Notification.objects.filter(target=user, is_read=False)

        for notif in notifications:
            notif.read()

        notifications_count = Notification.objects.filter(target=user, is_read=False).count()

        response = { 'unseen_total': notifications_count }
        return response


    # Rooms
    def leave_room(self, room):
        self.user_rooms.remove(room)
        self.save()

    def join_room(self, room):
        self.user_rooms.add(room)
        self.save()



# Application-wide Notification
class Notification(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actor', on_delete=models.CASCADE)
    verb = models.CharField(max_length=50)
    target = models.ForeignKey(settings.AUTH_USER_MODEL,  related_name='target', on_delete=models.CASCADE)
    executed_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    
    # Generic Foreign Key - so foreign model can be different models (eg. Announcement, File)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    action_obj = GenericForeignKey('content_type', 'object_id')

    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.actor.username} {self.verb}'

    def read(self):
        self.is_read = True
        self.save()

        return JsonResponse({ 'is_read' : True })

    class Meta:
        ordering = ['-executed_datetime']