# Generated by Django 3.1 on 2020-08-12 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0007_room_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='id',
            field=models.PositiveIntegerField(null=True, verbose_name='ID'),
        ),
    ]
