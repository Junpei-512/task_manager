# Generated by Django 5.1.1 on 2024-09-15 10:09

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_task_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='attachments/', verbose_name='Attached file'),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True, null=True, verbose_name='Deadline'),
        ),
        migrations.AlterField(
            model_name='task',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='task',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='Completed'),
        ),
        migrations.AlterField(
            model_name='task',
            name='progress',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Progress(%)'),
        ),
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='task',
            name='urgency',
            field=models.CharField(choices=[('low', '低'), ('medium', '中'), ('high', '高')], default='medium', max_length=6, verbose_name='Urgency'),
        ),
        migrations.CreateModel(
            name='ProgressHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.IntegerField(verbose_name='進捗')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='日時')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_history', to='tasks.task')),
            ],
        ),
    ]
