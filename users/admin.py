from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Avatar, Notification


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Avatar)
admin.site.register(Notification)