# Generated by Django 5.0.6 on 2024-05-17 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phystasks',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='phystasks',
            name='trust',
            field=models.BooleanField(default=False),
        ),
    ]
