# Generated by Django 3.1 on 2020-08-12 04:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_profile_user_rooms'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user_rooms_bak',
        ),
    ]
