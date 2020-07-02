from django.contrib import admin
from .models import File, Room

# Register your models here.
admin.site.register(Room)
admin.site.register(File)