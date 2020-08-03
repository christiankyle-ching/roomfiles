from django.core.exceptions import PermissionDenied

from users.models import User, Notification

# Model utils
def user_postable_is_owner(user, postable_obj):
    return user == postable_obj.posted_by

def user_postable_set_details(self, form):
    # inject posted_by as request.user
    form.instance.posted_by = self.request.user
    
    # inject room of postable
    form.instance.room = self.request.user.profile.room

    return form



def notify_users(self, verb=''):    
    users_in_room = User.active.filter(profile__room=self.room)

    for user in users_in_room:
        if user != self.posted_by:
            notification = Notification(actor=self.posted_by, verb=verb, action_obj=self, target=user)
            notification.save()

def read_object(user, obj_contenttype, obj_id):
    notification = Notification.objects.filter(
        action_obj_contenttype=obj_contenttype,
        action_obj_id=obj_id,
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
    # User should have same room and is not banned to view
    if user.profile.room == room:
        return True

    return False

def user_allowed_create_obj(user):
    return user.profile.room

def user_allowed_view_object(user, obj):
    # Check for constraints
    if user_allowed_in_room(user, obj.room):
        return True

    return False

def user_allowed_edit_object(user, obj):
    if user_postable_is_owner(user, obj):
        return True

    return False


