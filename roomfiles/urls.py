from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rooms import urls as rooms_urls

from django.contrib.auth import views as auth_views
from users import views as user_views
from users.views import NotificationListView, register, profile

urlpatterns = [
    # Rooms Urls
    path('', include(rooms_urls)),

    path('admin/', admin.site.urls),

    # User Urls
    path('account/', include([
        path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

        path('profile/', user_views.profile, name='profile'),
        path('settings/', user_views.settings, name='user-settings'),

        path('password-reset/', auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            html_email_template_name="users/password_reset_email.html",
            subject_template_name="users/password_reset_subject.txt",
            extra_email_context={'site_name': 'RoomFiles'},
            ),
            name='password_reset'),

        path('password-reset/done/',
            auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
            name='password_reset_done'),

        path('password-reset/<uidb64>/<token>/confirm/',
            auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
            name='password_reset_confirm'),

        path('password-reset/complete/',
            auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
            name='password_reset_complete'),
    
        path('password-change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html'), name='password_change'),
    
        path('password-change/success/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
    
    ])),
    

    
    # Notifications
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('seen/<str:model>/', user_views.api_seen_object, name='api-notif-seen'),

    path('register/', user_views.register, name='register'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
