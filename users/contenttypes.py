from django.contrib.contenttypes.models import ContentType


def get_ann_contenttype():
    return ContentType.objects.get_by_natural_key('rooms', 'announcement')

def get_file_contenttype():
    return ContentType.objects.get_by_natural_key('rooms', 'file')

