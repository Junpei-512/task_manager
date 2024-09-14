from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

URGENCY_CHOICES = [
    ('low', '低'),
    ('medium', '中'),
    ('high', '高'),
]

class Task(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    is_completed = models.BooleanField(_('Completed'), default=False)
    due_date = models.DateField(_('Deadline'), null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    urgency = models.CharField(_('Urgency'), max_length=6, choices=URGENCY_CHOICES, default='medium')
    progress = models.PositiveIntegerField(_('Progress(%)'), default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])  # 追加
    attachment = models.FileField(_('Attached file'), upload_to='attachments/', null=True, blank=True)  # 追加
    image = models.ImageField(_('Image'), upload_to='images/', null=True, blank=True)  # 追加
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subtasks', on_delete=models.CASCADE)  # 追加
     
    def __str__(self):
        return self.title
        
    def update_progress_from_subtasks(self):
        if self.subtasks.exists():
            total_progress = sum(subtask.progress for subtask in self.subtasks.all())
            self.progress = total_progress // self.subtasks.count()
            self.is_completed = True if self.progress >= 100 else False
            self.save()
            
        # 新しいメソッドを追加
    def get_bg_class(self):
        if self.is_completed:
            return 'bg-completed'
        elif self.due_date:
            days_left = (self.due_date - timezone.now().date()).days
            if days_left < 0:
                return 'bg-overdue'
            elif days_left < 1:
                return 'bg-less-than-24-hours'
            elif days_left < 3:
                return 'bg-less-than-72-hours'
        return ''
        
        # save メソッドのオーバーライド
    def save(self, *args, **kwargs):
        if self.is_completed:
            self.progress = 100
        super().save(*args, **kwargs)