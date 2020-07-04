# Model utils
def user_postable_is_owner(self):
    _file = self.get_object()
    return self.request.user == _file.posted_by

def user_postable_set_details(self, form):
    # inject posted_by as request.user
    form.instance.posted_by = self.request.user
    
    # inject room of postable
    form.instance.room = self.request.user.profile.room

    return form

def is_room_owner(self):
    _room = self.get_object()
    return self.request.user == _room.created_by

def set_room_details(self, form):
    # inject creator of room as request.user
    form.instance.created_by = self.request.user
    
    # inject room of file
    form.instance.room = self.request.user.profile.room

    return form

