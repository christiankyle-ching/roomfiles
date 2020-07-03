def is_file_owner(self):
    _file = self.get_object()
    return self.request.user == _file.uploaded_by

def set_file_details(self, form):
    # inject creator of file as request.user
    form.instance.uploaded_by = self.request.user
    
    # inject room of file
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
