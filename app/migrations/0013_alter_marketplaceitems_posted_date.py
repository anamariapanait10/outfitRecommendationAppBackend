# Generated by Django 4.2.9 on 2024-04-28 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_rename_outfit_id_marketplaceitems_outfit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketplaceitems',
            name='posted_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
