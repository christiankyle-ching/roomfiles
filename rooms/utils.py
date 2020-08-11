from django.core.exceptions import PermissionDenied
from django.apps import apps

from users.models import User, Notification
from .contenttypes import get_ann_contenttype, get_file_contenttype



def get_notification_model():
    # return apps.get_model('users', 'Notification')
    return Notification

# Model utils
def user_postable_is_owner(user, postable_obj):
    return user == postable_obj.posted_by

def user_postable_set_details(form, user, room):
    form.instance.posted_by = user
    form.instance.room = room

    return form



def notify_users(room_obj, verb=''):    
    users_in_room = room_obj.room.user_rooms.all()
    users_in_room = [ profile.user for profile in users_in_room ]

    for user in users_in_room:
        if user != room_obj.posted_by:
            notification = Notification(actor=room_obj.posted_by, verb=verb, action_obj=room_obj, target=user)
            notification.save()

def read_object(user, obj_contenttype, obj_id):
    notification = Notification.objects.filter(
        content_type=obj_contenttype,
        object_id=obj_id,
        target=user
        ).first()

    if notification:
        notification.read()

def notify_user(actor, action_obj, target, verb=''):
    notification = Notification(actor=actor, verb=verb, action_obj=action_obj, target=target)
    notification.save()
    


def user_is_room_owner(user, room):
    return user == room.created_by

def user_allowed_enter_room(user, room):
    return user not in room.banned_users.all()

def user_allowed_in_room(user, room):
    # User should have room included in user_rooms
    if room in user.profile.user_rooms.all():
        return True

    return False

def user_allowed_view_object(user, obj):
    # Check for constraints
    if user_allowed_in_room(user, obj.room):
        return True

    return False

def user_allowed_edit_object(user, obj):
    if user_postable_is_owner(user, obj):
        return True

    return False


