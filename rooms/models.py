from django.shortcuts import reverse
from django.utils.text import slugify

from django.db import models
from django.contrib.auth.models import User

import uuid

class Describable(models.Model):
    '''
    Abstract model for describable models.
    Fields:
        name - CharField
        description - TextField
    '''
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=1000)

    class Meta:
        abstract = True

class Room(Describable):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    slug = models.SlugField(default='', editable=False, max_length=100)

    def get_absolute_url(self):
        return reverse('room', kwargs={ 'pk' : self.pk, 'slug' : self.slug })

    def save(self, *args, **kwargs):
        # generate slug
        name = self.name
        self.slug = slugify(name, allow_unicode=True)

        super().save(*args, **kwargs)

class File(Describable):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, editable=False)

    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    upload_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    # raw_file = models.FileField(upload_to='files', storage=gd_storage)

    def get_absolute_url(self):
        return reverse('file', kwargs={ 'pk' : self.pk })