# Generated by Django 2.1.5 on 2020-04-27 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gamers', '0026_auto_20200425_0030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='user',
        ),
        migrations.RemoveField(
            model_name='gamer',
            name='notifications',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
