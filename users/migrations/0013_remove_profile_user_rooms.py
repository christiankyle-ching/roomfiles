# Generated by Django 3.1 on 2020-08-12 03:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_profile_user_rooms_bak'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user_rooms',
        ),
    ]
