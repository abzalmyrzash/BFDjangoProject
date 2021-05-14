# Generated by Django 3.1.6 on 2021-05-13 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0009_auto_20210513_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='to_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_friendrequests', to=settings.AUTH_USER_MODEL),
        ),
    ]
