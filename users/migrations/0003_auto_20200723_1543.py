# Generated by Django 3.0.7 on 2020-07-23 07:43

import django.contrib.auth.models
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200721_1135'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
                ('active', users.models.ActiveUserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='avatar',
            name='image',
        ),
        migrations.AddField(
            model_name='avatar',
            name='image_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
    ]
