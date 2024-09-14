from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from tasks.models import Task
from django.contrib.auth.models import User
from datetime import timedelta

class Command(BaseCommand):
    help = '期限が迫っているまたは過ぎているタスクのユーザーにメールを送信します。'

    def handle(self, *args, **options):
        now = timezone.now().date()
        in_72_hours = now + timedelta(hours=72)
        in_24_hours = now + timedelta(hours=24)

        # 期限が過ぎているタスク
        overdue_tasks = Task.objects.filter(due_date__lt=now, is_completed=False)

        # 期限まで24時間以内のタスク
        tasks_in_24_hours = Task.objects.filter(due_date__range=(now, in_24_hours), is_completed=False)

        # 期限まで72時間以内のタスク（24時間以内のタスクを除く）
        tasks_in_72_hours = Task.objects.filter(due_date__range=(in_24_hours, in_72_hours), is_completed=False)

        # ユーザーごとにタスクをまとめる
        users = User.objects.all()
        for user in users:
            user_overdue_tasks = overdue_tasks.filter(user=user)
            user_tasks_in_24_hours = tasks_in_24_hours.filter(user=user)
            user_tasks_in_72_hours = tasks_in_72_hours.filter(user=user)

            if user_overdue_tasks.exists() or user_tasks_in_24_hours.exists() or user_tasks_in_72_hours.exists():
                # メールの内容をテンプレートで作成
                subject = '【タスク管理アプリ】タスクの期限に関するお知らせ'
                message = render_to_string('tasks/email_reminder.html', {
                    'user': user,
                    'overdue_tasks': user_overdue_tasks,
                    'tasks_in_24_hours': user_tasks_in_24_hours,
                    'tasks_in_72_hours': user_tasks_in_72_hours,
                })
                recipient_list = [user.email]

                # メールを送信
                send_mail(subject, message, None, recipient_list)
                self.stdout.write(self.style.SUCCESS(f'ユーザー {user.username} にメールを送信しました。'))
