# Generated by Django 4.2.9 on 2024-05-02 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_stats'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wornoutfits',
            old_name='user_id',
            new_name='user',
        ),
    ]
