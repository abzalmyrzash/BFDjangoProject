# Generated by Django 3.1.6 on 2021-05-14 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20210513_1902'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendrequest',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='groupinvite',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='groupjoinrequest',
            unique_together=set(),
        ),
    ]