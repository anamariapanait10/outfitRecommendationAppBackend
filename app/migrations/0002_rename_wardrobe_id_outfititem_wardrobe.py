# Generated by Django 4.2.9 on 2024-03-26 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='outfititem',
            old_name='wardrobe_id',
            new_name='wardrobe',
        ),
    ]
