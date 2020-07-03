from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Room
from users.models import Profile

@receiver(post_save, sender=Room)
def create_profile(sender, instance, created, **kwargs):
    # if room is created
    if created:
        # assign room also to the one who created it, then save profile
        instance.created_by.profile.room = instance
        instance.created_by.profile.save()
        
