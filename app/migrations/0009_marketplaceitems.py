# Generated by Django 4.2.9 on 2024-04-25 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_wornoutfits_bottom_alter_wornoutfits_shoes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketplaceItems',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(max_length=30)),
                ('images', models.TextField(blank=True, null=True)),
                ('condition', models.CharField(max_length=30)),
                ('size', models.CharField(max_length=30)),
                ('brand', models.CharField(max_length=30)),
                ('posted_date', models.DateField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('outfit_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.outfititem')),
            ],
        ),
    ]
