# Generated by Django 3.0.7 on 2020-07-30 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200723_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action_obj_id',
            field=models.CharField(max_length=64),
        ),
    ]