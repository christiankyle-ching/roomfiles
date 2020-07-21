from django.db import models
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings


def get_ann_contenttype():
    return ContentType.objects.get_by_natural_key('rooms', 'announcement')

def get_file_contenttype():
    return ContentType.objects.get_by_natural_key('rooms', 'file')



class ActiveUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    objects = UserManager()
    active = ActiveUserManager()

class Avatar(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='avatars')

    def __str__(self):
        return f'{self.name} Avatar'

class ActiveProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__is_active=True)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)

    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, null=True, editable=False)

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


# Application-wide Notification
class Notification(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actor', on_delete=models.CASCADE)
    verb = models.CharField(max_length=50)
    target = models.ForeignKey(settings.AUTH_USER_MODEL,  related_name='target', on_delete=models.CASCADE)
    executed_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    
    # Generic Foreign Key - so foreign model can be different models (eg. Announcement, File)
    action_obj_contenttype = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    action_obj_id = models.PositiveIntegerField()
    action_obj = GenericForeignKey('action_obj_contenttype', 'action_obj_id')

    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.actor.username} {self.verb}'

    def read(self):
        self.is_read = True
        self.save()

        return JsonResponse({ 'is_read' : True })
