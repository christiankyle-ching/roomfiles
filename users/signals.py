from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # if post request is creation,
    if created:
        # then create new Profile with user object of profile set to instance of User
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    # update the instance(User).profile by save()
    instance.profile.save()
