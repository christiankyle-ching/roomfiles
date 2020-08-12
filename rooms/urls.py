from django.urls import path, include

from . import views
from users import views as user_views
from .views import (
    RoomDetailView, RoomCreateView, RoomUpdateView, RoomListView,
    FileDetailView, FileCreateView, FileUpdateView, FileDeleteView,
    AnnouncementCreateView, AnnouncementUpdateView, AnnouncementDeleteView, AnnouncementListView,
    )

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    

    # User Room Urls
    path('rooms/', RoomListView.as_view(template_name="rooms/user_rooms.html"), name="user-rooms"),
    path('room/create/', RoomCreateView.as_view(), name='room-create'),
    path('room/join/', views.join_room, name='room-join'),

    # Specific Room
    path('room/<int:room_pk>-<str:room_slug>/', include([

        path('', RoomDetailView.as_view(), name='room'),
        path('edit/', RoomUpdateView.as_view(), name='room-edit'),
        path('anns/', AnnouncementListView.as_view(), name='room-anns'),
        path('leave/', views.leave_room, name='room-leave'),

        
        # File Urls
        path('file/upload/', FileCreateView.as_view(), name='file-upload'),
        path('file/<int:file_pk>/', include([
            path('', FileDetailView.as_view(), name='file'),
            path('edit/', FileUpdateView.as_view(), name='file-edit'),
            path('delete/', FileDeleteView.as_view(), name='file-delete'),
        ])),


        # Announcement Urls
        path('ann/post/', AnnouncementCreateView.as_view(), name='ann-create'),
        path('ann/<int:ann_pk>/', include([
            path('edit/', AnnouncementUpdateView.as_view(), name='ann-edit'),
            path('delete/', AnnouncementDeleteView.as_view(), name='ann-delete'),
            
            path('api-like/', views.api_toggle_like, name='api-ann-like'),
        ])),
        
        # Read Announcement / File
        path('read/<str:model_type>/', user_views.api_read_objects, name='api-notif-read-objects'),
    ])),
    


]

