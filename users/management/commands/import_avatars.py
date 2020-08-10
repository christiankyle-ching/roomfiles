from django.core.management.base import BaseCommand
from django.conf import settings
import os, re

from users.models import Avatar

class Command(BaseCommand):
    help = 'Imports all images located in settings.BASE_DIR/assets/avatars as Avatar objects'

    ALLOWED_FILETYPES = ('.png', '.webp', '.jpeg', '.jpg')
    AVATARS_DIR = os.path.join(settings.BASE_DIR, 'rooms', 'static', 'images', 'avatars')

    def handle(self, *args, **kwargs):
        print('CLEARING DATABASE...')
        Avatar.objects.all().delete()

        print('ADDING FILES FROM ASSETS')
        self.import_all()

    def import_all(self):
        for _file in os.listdir(self.AVATARS_DIR):
            _matches = re.search('(.*)(\..*)$', _file)

            if _matches.groups()[1] == None: continue

            filename = _matches.groups()[0].capitalize()
            file_extension = _matches.groups()[1]

            if file_extension.lower() in self.ALLOWED_FILETYPES:
                print(f'ADDING: {filename} Avatar from "{self.AVATARS_DIR + _file}"')

                avatar = Avatar(name=filename, image_url=settings.STATIC_URL+'images/avatars/'+_file)
                avatar.save()
