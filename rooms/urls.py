from django.urls import path, include

from . import views
from .views import (
    RoomDetailView, RoomCreateView, RoomUpdateView,
    FileDetailView, FileCreateView, FileUpdateView, FileDeleteView,
    AnnouncementCreateView, AnnouncementUpdateView, AnnouncementDeleteView, AnnouncementListView,
    )

urlpatterns = [
    path('', views.home, name='home'),

    path('room/landing/', views.room_landing, name='room-landing'),
    path('room/join/', views.join_room, name='room-join'),

    # Room Urls
    path('room/create/', RoomCreateView.as_view(), name='room-create'),
    path('room/<uuid:pk>-<str:slug>/', include([
        path('', RoomDetailView.as_view(), name='room'),
        path('edit/', RoomUpdateView.as_view(), name='room-edit'),
        path('anns/', AnnouncementListView.as_view(), name='room-anns'),
    ])),
    path('room/leave/', views.leave_room, name='room-leave'),

    # File Urls
    path('file/upload/', FileCreateView.as_view(), name='file-upload'),
    path('file/<int:pk>/', include([
        path('', FileDetailView.as_view(), name='file'),
        path('edit/', FileUpdateView.as_view(), name='file-edit'),
        path('delete/', FileDeleteView.as_view(), name='file-delete'),
    ])),

    path('ann/post/', AnnouncementCreateView.as_view(), name='ann-create'),
    path('ann/<int:pk>/', include([
        path('edit/', AnnouncementUpdateView.as_view(), name='ann-edit'),
        path('post/', AnnouncementDeleteView.as_view(), name='ann-delete'),
        path('like-api/', views.toggle_announcement_api, name='ann-like-api'),
    ])),

]

