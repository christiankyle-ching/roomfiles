from django.conf import settings
from django.core.exceptions import ValidationError
import re

def limit_file_size(file):
    if int(file.size) > settings.MAX_FILE_SIZE:
        raise ValidationError(f'File size exceeds { settings.MAX_FILE_SIZE / (1024**2) }MB limit')

def allowed_file_type(file):
    file_type = re.search('\.([0-9a-z]+)$', file.name, re.I).group(1)
    if file_type.lower() not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(f'File type "{file_type.upper()}" is not supported')
