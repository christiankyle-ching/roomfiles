from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    # If ready, import signals
    def ready(self):
        import users.signals
