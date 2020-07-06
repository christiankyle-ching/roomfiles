# Generated by Django 3.0.7 on 2020-07-04 01:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rooms', '0012_announcement_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='posted_by',
            new_name='posted_by',
        ),
        migrations.AddField(
            model_name='announcement',
            name='posted_by',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]