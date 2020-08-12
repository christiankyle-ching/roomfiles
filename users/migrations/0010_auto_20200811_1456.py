# Generated by Django 3.1 on 2020-08-11 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200809_1612'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='avatar',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-executed_datetime']},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['user__username']},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username']},
        ),
    ]