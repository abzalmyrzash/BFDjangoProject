# Generated by Django 3.1.6 on 2021-05-12 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_', '0005_auto_20210512_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'male'), (2, 'female')], null=True, verbose_name='Пол'),
        ),
    ]
