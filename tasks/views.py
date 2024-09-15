from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Task, ProgressHistory
from .forms import TaskForm, CustomUserCreationForm
from django.db.models import Q
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from django.views.decorators.http import require_POST
from django.contrib.auth import login  # 追加
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.utils.dateformat import DateFormat
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    # クエリパラメータの取得
    sort_by = request.GET.get('sort_by')
    min_progress = request.GET.get('min_progress')
    max_progress = request.GET.get('max_progress')
    query = request.GET.get('q')  # 検索キーワード
    due_date = request.GET.get('due_date')  # 期限フィルタ
    urgency = request.GET.get('urgency')
    is_completed = request.GET.get('is_completed')  # 完了状態のフィルタ

    # フィルタリングの適用
    if query:
        tasks = tasks.filter(title__icontains=query)

    if due_date:
        tasks = tasks.filter(due_date=due_date)
        
    if urgency:
        tasks = tasks.filter(urgency=urgency)

    if is_completed == 'true':
        tasks = tasks.filter(is_completed=True)
    elif is_completed == 'false':
        tasks = tasks.filter(is_completed=False)

    if min_progress or max_progress:
        min_progress = int(min_progress) if min_progress else 0
        max_progress = int(max_progress) if max_progress else 100
        tasks = tasks.filter(progress__gte=min_progress, progress__lte=max_progress)

    # ソートの適用
    if sort_by == 'progress_asc':
        tasks = tasks.order_by('progress')
    elif sort_by == 'progress_desc':
        tasks = tasks.order_by('-progress')
    else:
        tasks = tasks.order_by('due_date')  # デフォルトで期限順にソート

    # ページネーションの追加
    paginator = Paginator(tasks, 10)  # 1ページあたり10件表示
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'tasks': page_obj,
        'now': timezone.now(),
        # 他のコンテキスト
    }

    return render(request, 'tasks/task_list.html', context)
    
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def task_create(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user  # ユーザーを設定
            task.is_completed = True if task.progress >= 100 else False
            task.save()
            form.save_m2m()

            # 親タスクの進捗を更新
            if task.parent:
                task.parent.update_progress_from_subtasks()
            # 進捗が100%の場合、自動的に完了とする
            if task.progress >= 100:
                task.is_completed = True
            task.save()
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            form.save_m2m()

            # 親タスクの進捗を更新
            if task.parent:
                task.parent.update_progress_from_subtasks()

            # 完了状態が False の場合、進捗が 100 であれば 99 に設定
            if not task.is_completed and task.progress >= 100:
                task.progress = 95
            # 進捗に応じて完了状態を更新
            if task.progress >= 100:
                task.is_completed = True
            else:
                task.is_completed = False
            # 完了状態がTrueで、完了日時が設定されていない場合にのみ完了日時を記録
            if form.cleaned_data['is_completed'] and not task.completed_at:
                task.completed_at = timezone.now()
            # 進捗が100%以下なら完了日時をリセット
            elif not form.cleaned_data['is_completed']:
                task.completed_at = None
            
            if task.is_completed and not task.can_be_uncompleted():
                form.add_error(None, _('完了から72時間以上経過しているため、未完了に戻せません。'))
            else:
                form.save()
                return redirect('tasks:task_detail', pk=pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks:task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = True
    task.save()
    return redirect('tasks:task_list')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ユーザーをログインさせる
            messages.success(request, _('Your account was created.'))
            return redirect('tasks:task_list')  # タスク一覧ページにリダイレクト
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
    
@login_required
@require_POST
def update_progress(request):
    with transaction.atomic():
        logger.debug('update_progress ビューが呼び出されました')
        logger.debug('POST データ: %s', request.POST)
        # タスクの進捗を更新
        for key, value in request.POST.items():
            if key.startswith('progress_'):
                task_id = key.split('_')[1]
                try:
                    task = get_object_or_404(Task, id=task_id, user=request.user)
                    new_progress = int(value)
                    if new_progress < 0:
                        new_progress = 0
                    elif new_progress > 100:
                        new_progress = 100
                    task.progress = new_progress
                    # 完了状態の自動更新
                    if task.progress >= 100:
                        task.complete()  # 完了メソッドで完了日時を記録
                    else:
                        if task.can_be_uncompleted():  # 72時間以内なら「未完了」に戻せる
                            task.is_completed = False
                            task.completed_at = None  # 完了日時をリセット
                    task.save()
                    # 進捗履歴を記録
                    ProgressHistory.objects.create(task=task, progress=task.progress)
                except (Task.DoesNotExist, ValueError):
                    continue  # タスクが存在しない場合はスキップ

    return redirect('tasks:task_list')
    
@login_required
def task_progress_chart(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    progress_history = task.progress_history.order_by('timestamp')

    # 日時と進捗のリストを作成（ISO 8601形式）
    timestamps = [entry.timestamp.strftime("%Y-%m-%dT%H:%M:%S") for entry in progress_history]
    progress_values = [entry.progress for entry in progress_history]

    context = {
        'task': task,
        'timestamps': timestamps,
        'progress_values': progress_values,
    }
    return render(request, 'tasks/task_progress_chart.html', context)    

    
class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Your account was created.'))
            return redirect('tasks:task_list')
        return render(request, 'registration/register.html', {'form': form})
        