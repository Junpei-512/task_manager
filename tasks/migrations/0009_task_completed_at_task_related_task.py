# Generated by Django 5.1.1 on 2024-09-15 12:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_alter_task_attachment_alter_task_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='related_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='related_tasks', to='tasks.task'),
        ),
    ]
