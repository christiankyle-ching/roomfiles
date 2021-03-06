# Generated by Django 3.1 on 2020-08-12 03:27

import django.contrib.postgres.fields
from django.db import migrations, models, transaction

def populate_user_rooms_bak(apps, schema_editor):
    Profile = apps.get_model('users', 'Profile')

    with transaction.atomic():

        for profile in Profile.objects.all():

            room_codes = []
            for room in profile.user_rooms.all():
                room_codes.append(room.pk)

            profile.user_rooms_bak = room_codes
            profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20200811_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user_rooms_bak',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.UUIDField(), blank=True, default=list, size=None),
        ),
        migrations.RunPython(populate_user_rooms_bak, reverse_code=migrations.RunPython.noop),
    ]
