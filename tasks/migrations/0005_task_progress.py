# Generated by Django 5.1.1 on 2024-09-13 14:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_alter_task_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='progress',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='進捗状況（%）'),
        ),
    ]
