# Generated by Django 4.2.10 on 2025-03-22 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersettings',
            name='performance_enabled',
            field=models.BooleanField(default=True, help_text='Enable or disable performance tracking and gain/loss calculations', verbose_name='Enable Performance Tracking'),
        ),
    ]
