# Generated by Django 4.2.9 on 2024-04-30 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_marketplaceitems_brand_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketplaceitems',
            name='brand',
            field=models.CharField(default='nike', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marketplaceitems',
            name='condition',
            field=models.CharField(default='New', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marketplaceitems',
            name='description',
            field=models.TextField(default='asd'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marketplaceitems',
            name='location',
            field=models.CharField(default='Bucharest', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marketplaceitems',
            name='posted_date',
            field=models.DateTimeField(default='2024-04-25 16:05:05.171000'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marketplaceitems',
            name='price',
            field=models.DecimalField(decimal_places=2, default=10.0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marketplaceitems',
            name='size',
            field=models.CharField(default='S', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marketplaceitems',
            name='status',
            field=models.CharField(default='Available', max_length=30),
            preserve_default=False,
        ),
    ]
