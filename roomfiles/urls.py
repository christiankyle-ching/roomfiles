from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rooms import urls as rooms_urls

from django.contrib.auth import views as auth_views
from users import views as user_views
from users.views import NotificationListView

urlpatterns = [
    # Rooms Urls
    path('', include(rooms_urls)),

    path('admin/', admin.site.urls),

    # User Urls
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),

    path('register/', user_views.register, name='register'),

    # Avatar Fetch Url
    path('avatar/<int:pk>/', user_views.avatar_preview, name='avatar-preview')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
