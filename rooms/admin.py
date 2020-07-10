from django.contrib import admin
from .models import File, Room, Announcement, Notification



admin.site.register(Room)
admin.site.register(File)
admin.site.register(Announcement)
admin.site.register(Notification)