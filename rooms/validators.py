from roomfiles.settings import MAX_FILE_SIZE, ALLOWED_FILE_TYPES
from django.core.exceptions import ValidationError
import re

def limit_file_size(file):
    if int(file.size) > MAX_FILE_SIZE:
        raise ValidationError('File size exceeds {}MB limit'.format( (MAX_FILE_SIZE / (1024**2)) ))

def allowed_file_type(file):
    file_type = re.search('\.([0-9a-z]+)$', file.name, re.I).group(1)
    if file_type.lower() not in ALLOWED_FILE_TYPES:
        raise ValidationError('File type "{}" is not supported'.format(file_type))
