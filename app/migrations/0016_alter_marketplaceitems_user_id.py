# Generated by Django 4.2.9 on 2024-04-30 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_marketplaceitems_brand_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketplaceitems',
            name='user_id',
            field=models.CharField(max_length=250),
        ),
    ]
