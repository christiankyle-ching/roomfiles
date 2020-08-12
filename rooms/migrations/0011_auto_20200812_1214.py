# Generated by Django 3.1 on 2020-08-12 04:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0010_auto_20200812_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name='room',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
