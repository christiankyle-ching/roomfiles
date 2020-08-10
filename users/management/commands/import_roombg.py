from django.core.management.base import BaseCommand
from django.conf import settings
import os, re

from rooms.models import RoomBackground

class Command(BaseCommand):
    help = 'Imports all images located in settings.BASE_DIR/assets/room-backgrounds as RoomBackground objects'

    ALLOWED_FILETYPES = ('.png', '.webp', '.jpeg', '.jpg')
    ROOM_BG_DIR = os.path.join(settings.BASE_DIR, 'rooms', 'static', 'images', 'room-backgrounds')

    def handle(self, *args, **kwargs):
        print('CLEARING DATABASE...')
        RoomBackground.objects.all().delete()

        print('ADDING FILES FROM ASSETS')
        self.import_all()

    def import_all(self):
        for _file in os.listdir(self.ROOM_BG_DIR):
            _matches = re.search('(.*)(\..*)$', _file)

            if _matches.groups()[1] == None: continue

            filename = _matches.groups()[0].capitalize()
            file_extension = _matches.groups()[1]

            if file_extension.lower() in self.ALLOWED_FILETYPES:
                print(f'ADDING: {filename} RoomBackground from "{self.ROOM_BG_DIR + _file}"')

                roombg = RoomBackground(name=filename, image_url=settings.STATIC_URL+'images/room-backgrounds/'+_file)
                roombg.save()
