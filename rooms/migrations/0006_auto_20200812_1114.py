# Generated by Django 3.1 on 2020-08-12 03:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0005_auto_20200811_1454'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='id',
            new_name='uuid',
        ),
    ]