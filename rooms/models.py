from django.shortcuts import reverse, get_object_or_404
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse

from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

import uuid
from .validators import limit_file_size, allowed_file_type

# Init Google Drive Storage
from gdstorage.storage import GoogleDriveStorage
gd_storage = GoogleDriveStorage()

from .utils import notify_users, notify_user, user_allowed_view_object, get_notification_model
from django.conf import settings




class RoomBackground(models.Model):
    class Meta:
        ordering = ['name']
    
    name = models.CharField(max_length=30)
    image_url = models.URLField()

    def __str__(self):
        return f'{self.name} Background Image'

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
from django.contrib.postgres.fields import ArrayField
class Room(Describable):
    class Meta:
        ordering = ['name']
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    uuid = models.UUIDField(editable=False, default=uuid.uuid4)
    slug = models.SlugField(default='', editable=False, max_length=100)

    banned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="banned_users", editable=False)
    # banned_users_bak = ArrayField(models.PositiveIntegerField(), blank=True, default=list)
    background = models.ForeignKey(RoomBackground, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Room {self.name}'

    def get_absolute_url(self, tab=""):
        _url_hash = f'#{tab}' if tab != "" else ""
        return reverse('room', kwargs={ 'room_pk' : self.pk, 'room_slug' : self.slug }) + _url_hash
    
    def save(self, *args, **kwargs):
        # generate slug from name
        name = self.name
        self.slug = slugify(name, allow_unicode=True)

        super().save(*args, **kwargs)

    
    # Toggle a user ban status
    def toggle_ban(self, user):
        if user:
            response = { 'banned': False, 'message': '' }

            if self.created_by == user:
                response['message'] = 'You cannot ban yourself.'
                return response

            if user in self.banned_users.all():
                self.banned_users.remove(user)
                response['banned'] = False
                response['message'] = f'Successfully remove {user.username} from being banned.'
            else:
                self.banned_users.add(user)
                response['banned'] = True
                response['message'] = f'Successfully banned {user.username} in your room.'

                user.profile.user_rooms.remove(self)
                user.profile.save()

                # FIX: Cannot add notification with room action_obj.
                # REASON: Primary Key of Room (UUID) is not compatible with Notification's action_obj_id (int)
                # SOLUTION: Add Auto-Increment PK for Room

                notify_user(target=user, actor=self.created_by, action_obj=self, verb='banned you in')

            self.save()
            return response
        else:
            return { 'message': 'Invalid User ID' }

    # Change background
    def change_background(self, roombg_id):
        roombackground = get_object_or_404(RoomBackground, pk=roombg_id)
        self.background = roombackground
        self.save()

    
    def get_people(self):
        return self.user_rooms.all()

    def get_banned_people(self):
        return [user.profile for user in self.banned_users.all()]

    def get_files(self, search=None):
        files_qs = File.objects.filter(room=self).defer('raw_file')
        if search:
            files_qs = files_qs.filter(
                Q(posted_by__username__icontains=search) |
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        return files_qs

    def get_announcements(self, search=None, sort=None):        
        anns_qs = Announcement.objects.filter(room=self)
        if search:
            anns_qs = anns_qs.filter(
                Q(posted_by__username__icontains=search) |
                Q(content__icontains=search)
            )

        if sort:
            if sort == 'date-desc':
                anns_qs = anns_qs.order_by('-posted_datetime')
            else:
                anns_qs = anns_qs.order_by('posted_datetime')
        
        return anns_qs

    @property
    def notification_text(self):
        return self.name

    @property
    def users_count(self):
        return self.user_rooms.count()


# Abstract
class Room_Object(models.Model):
    """
    Abstract model for models exclusive to particular rooms.
    Fields:
        room - ForeignKey(Room)
    """
    # room = models.ForeignKey(Room, on_delete=models.CASCADE, editable=False)
    # room = models.UUIDField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, editable=False, null=True)
    # notifications = GenericRelation(
    #     get_notification_model(),
    #     related_query_name='rooms_object',
    #     object_id_field='object_id',
    #     content_type_field='content_type'
    #     )

    class Meta:
        abstract = True

class User_Postable(models.Model):
    """
    Abstract model for models postable by a user.
    Fields:
        posted_by - ForeignKey(User)
        posted_datetime - DateTimeField(auto_now_add = True)
    """
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    posted_datetime = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True

class User_Likable(models.Model):
    """
    Abstract model for models likable by a user.
    Fields:
        liked_by - Many-to-Many Field to Users
    """
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_by", editable=False)
    
    class Meta:
        abstract = True



# Models
class File(Room_Object, User_Postable, Describable):
    class Meta:
        ordering = ['-posted_datetime']

    raw_file = models.FileField(
        upload_to='files', storage=gd_storage,
        validators=[limit_file_size, allowed_file_type],
        verbose_name='File',
        )
    notifications = GenericRelation(
        get_notification_model(),
        related_query_name='rooms_file',
        object_id_field='object_id',
        content_type_field='content_type'
        )

    def get_absolute_url(self):
        return reverse('file', kwargs={ 'room_pk': self.room.pk, 'room_slug': self.room.slug, 'file_pk': self.pk })

    def __str__(self):
        return f'File {self.name}'

    def notify_users(self):
        notify_users(self, verb='uploaded')

    @property
    def notification_text(self):
        return f'in {self.room.name} ({self.name[:15]}...)'


class Announcement(Room_Object, User_Postable, User_Likable):    
    class Meta:
        ordering = ['-posted_datetime']

    content = models.TextField(blank=False, max_length=1000)
    notifications = GenericRelation(
        get_notification_model(),
        related_query_name='rooms_announcement',
        object_id_field='object_id',
        content_type_field='content_type'
        )

    def __str__(self):
        return f'{self.posted_by}: "{self.content[:30]}..."'

    def get_absolute_url(self):
        return self.room.get_absolute_url(tab='ann')

    def toggle_like(self, user):
        # if not self.room == user.profile.room:
        if not user_allowed_view_object(user, self):
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
        }

        return response

    def notify_users(self):
        notify_users(self, verb='posted')
    

    @property
    def notification_text(self):
        return f'in {self.room.name} ("{self.content[:15]}...")'



