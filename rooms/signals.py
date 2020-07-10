from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Room, Announcement, File
from users.models import Profile

@receiver(post_save, sender=Room)
def create_profile(sender, instance, created, **kwargs):
    # if room is created
    if created:
        # assign room also to the one who created it, then save profile
        instance.created_by.profile.room = instance
        instance.created_by.profile.save()
        
@receiver(post_save, sender=Announcement)
def create_announcement(sender, instance, created, **kwargs):
    # if announcement is created
    if created:
        # notify users
        instance.notify_users()

@receiver(post_save, sender=File)
def create_file(sender, instance, created, **kwargs):
    # if file is uploaded
    if created:
        # notify users
        instance.notify_users()
