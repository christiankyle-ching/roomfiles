# Generated by Django 3.1 on 2020-08-12 04:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0012_room_banned_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='banned_users_bak',
        ),
    ]
