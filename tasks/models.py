from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

URGENCY_CHOICES = [
    ('low', '低'),
    ('medium', '中'),
    ('high', '高'),
]

class Task(models.Model):
    title = models.CharField('タイトル', max_length=200)
    description = models.TextField('説明', blank=True)
    is_completed = models.BooleanField('完了', default=False)
    due_date = models.DateField('期限', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    urgency = models.CharField('緊急度', max_length=6, choices=URGENCY_CHOICES, default='medium')
    progress = models.PositiveIntegerField('進捗状況（%）', default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])  # 追加
    attachment = models.FileField('添付ファイル', upload_to='attachments/', null=True, blank=True)  # 追加
    image = models.ImageField('画像', upload_to='images/', null=True, blank=True)  # 追加
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subtasks', on_delete=models.CASCADE)  # 追加
     
    def __str__(self):
        return self.title
        
    def update_progress_from_subtasks(self):
        if self.subtasks.exists():
            total_progress = sum(subtask.progress for subtask in self.subtasks.all())
            self.progress = total_progress // self.subtasks.count()
            self.is_completed = True if self.progress >= 100 else False
            self.save()