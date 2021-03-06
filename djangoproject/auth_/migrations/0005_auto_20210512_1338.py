# Generated by Django 3.1.6 on 2021-05-12 07:38

from django.db import migrations, models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth_', '0004_profile_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='photo',
        ),
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars', validators=[utils.validators.validate_size, utils.validators.validate_extension]),
        ),
    ]
