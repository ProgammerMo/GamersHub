# Generated by Django 2.1.5 on 2020-04-24 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamers', '0020_auto_20200424_0325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='abbreviation',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.RemoveField(
            model_name='game',
            name='users',
        ),
        migrations.AddField(
            model_name='game',
            name='users',
            field=models.ManyToManyField(to='gamers.Gamer_ID'),
        ),
    ]