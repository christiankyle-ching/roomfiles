from django.contrib import admin
from .models import File, Room, Announcement

# Register your models here.
admin.site.register(Room)
admin.site.register(File)
admin.site.register(Announcement)