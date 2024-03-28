# Generated by Django 4.2.9 on 2024-03-26 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_wardrobe_id_outfititem_wardrobe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outfititem',
            name='name',
        ),
        migrations.RemoveField(
            model_name='outfititem',
            name='season',
        ),
        migrations.RemoveField(
            model_name='outfititem',
            name='size',
        ),
        migrations.AddField(
            model_name='outfititem',
            name='occasions',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='outfititem',
            name='seasons',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='outfititem',
            name='subCategory',
            field=models.CharField(default="", max_length=30),
            preserve_default=False,
        ),
    ]
