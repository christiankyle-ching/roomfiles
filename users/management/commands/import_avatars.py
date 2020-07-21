from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
import os, re
from roomfiles.settings import BASE_DIR, MEDIA_ROOT

from users.models import Avatar

class Command(BaseCommand):
    help = 'Imports all images located in BASE_DIR/assets/avatars as Avatar objects'

    _assets_dir = os.path.join(BASE_DIR, 'assets', 'avatars')

    def handle(self, *args, **kwargs):
        print('CLEARING DATABASE...')
        Avatar.objects.all().delete()

        print('CLEARING UPLOADED FILES...')
        self.clear_dir()

        print('ADDING FILES FROM ASSETS')
        self.import_all()

    def import_all(self):
        for _file in os.listdir(self._assets_dir):
            _matches = re.search('(.*)(\..*)$', _file)

            if _matches.groups()[1] == None: continue

            filename = _matches.groups()[0].capitalize()
            file_extension = _matches.groups()[1]

            if '.png' == file_extension.lower():
                _file_dir = os.path.join(self._assets_dir, _file)

                print(f'ADDING: {filename} Avatar at "{_file_dir}"')
                _tmp_obj = Avatar(name=filename)
                _tmp_obj.image.save(_file, File(open(_file_dir, 'rb')))

    def clear_dir(self):
        _media_avatars_dir = os.path.join(MEDIA_ROOT, 'avatars')

        for _file in os.listdir(_media_avatars_dir):
            _file_dir = os.path.join(_media_avatars_dir, _file)
            print('DELETING: ', _file_dir)
            os.remove(_file_dir)
