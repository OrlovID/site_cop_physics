# Generated by Django 5.0.6 on 2024-05-17 22:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_alter_phystasks_complexity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phystasks',
            name='answer',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='phystasks',
            name='author',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='phystasks',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='phystasks',
            name='theme',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.physthemes'),
        ),
        migrations.AlterField(
            model_name='physthemes',
            name='theme',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
