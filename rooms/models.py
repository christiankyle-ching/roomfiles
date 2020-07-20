from django.shortcuts import reverse, get_object_or_404
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

import uuid
from .validators import limit_file_size, allowed_file_type

# Init Google Drive Storage
from gdstorage.storage import GoogleDriveStorage
gd_storage = GoogleDriveStorage()



# Abstract
class Describable(models.Model):
    """
    Abstract model for describable models.
    Fields:
        name - CharField
        description - TextField
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=1000)

    class Meta:
        abstract = True

# Model
class Room(Describable):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    slug = models.SlugField(default='', editable=False, max_length=100)

    def get_absolute_url(self, tab=""):
        _url_hash = f'#{tab}' if tab != "" else ""
        return reverse('room', kwargs={ 'pk' : self.pk, 'slug' : self.slug }) + _url_hash
        
    def save(self, *args, **kwargs):
        # generate slug from name
        name = self.name
        self.slug = slugify(name, allow_unicode=True)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Room {self.name}'



# Abstract
class Room_Object(models.Model):
    """
    Abstract model for models exclusive to particular rooms.
    Fields:
        room - ForeignKey(Room)
    """
    room = models.ForeignKey(Room, on_delete=models.CASCADE,) #editable=False)

    class Meta:
        abstract = True

# Abstract
class User_Postable(models.Model):
    """
    Abstract model for models postable by a user.
    Fields:
        posted_by - ForeignKey(User)
        posted_datetime - DateTimeField(auto_now_add = True)
    """
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE,) #editable=False)
    posted_datetime = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True

class User_Likable(models.Model):
    """
    Abstract model for models likable by a user.
    Fields:
        liked_by - Many-to-Many Field to Users
    """
    liked_by = models.ManyToManyField(User, related_name="liked_by") #editable=False)
    
    class Meta:
        abstract = True



# Models
class File(Describable, User_Postable, Room_Object):
    raw_file = models.FileField(
        upload_to='files', storage=gd_storage,
        validators=[limit_file_size, allowed_file_type],
        verbose_name='File',
        )

    def get_absolute_url(self):
        return reverse('file', kwargs={ 'pk' : self.pk })

    def __str__(self):
        return f'File {self.name}'

    def notify_users(self):
        users_in_room = User.objects.filter(profile__room=self.room)

        for user in users_in_room:
            if user != self.posted_by:
                notification = Notification(actor=self.posted_by, verb='uploaded', action_obj=self, target=user)
                notification.save()

    @property
    def notification_name(self):
        return self.name


class Announcement(Room_Object, User_Postable, User_Likable):    
    content = models.TextField(blank=False, max_length=1000)

    def __str__(self):
        return f'{self.posted_by}: "{self.content[:30]}..."'

    def get_absolute_url(self):
        return self.room.get_absolute_url(tab='ann')

    def toggle_like(self, user):
        if not self.room == user.profile.room:
            raise PermissionDenied()

        if user in self.liked_by.all():
            self.liked_by.remove(user)
            liked = False
        else:
            self.liked_by.add(user)
            liked = True
        
        self.save()

        response = {
            'liked': liked,
            'new_like_count': self.liked_by.count(),
            'redirect_href': self.get_absolute_url()
        }

        return response

    def notify_users(self):
        users_in_room = User.objects.filter(profile__room=self.room)

        for user in users_in_room:
            if user != self.posted_by:
                notification = Notification(actor=self.posted_by, verb='posted', action_obj=self, target=user)
                notification.save()
    
    

    @property
    def notification_name(self):
        return self.content[:30]


# Application-wide Notification
class Notification(models.Model):
    actor = models.ForeignKey(User, related_name='actor', on_delete=models.CASCADE)
    verb = models.CharField(max_length=50)
    target = models.ForeignKey(User,  related_name='target', on_delete=models.CASCADE)
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

    

