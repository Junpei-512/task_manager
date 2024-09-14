from django.views import View
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Task
from .forms import TaskForm, CustomUserCreationForm
from django.db.models import Q
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from django.views.decorators.http import require_POST
from django.contrib.auth import login  # 追加
from django.contrib import messages
from django.utils import timezone

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
            task.save()
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
    print('update_progress ビューが呼び出されました')
    print('POST データ:', request.POST)
    # タスクの進捗を更新
    for key, value in request.POST.items():
        if key.startswith('progress_'):
            task_id = key.split('_')[1]
            progress = value
            try:
                task = Task.objects.get(pk=task_id, user=request.user)
                task.progress = int(progress)
                task.is_completed = True if int(progress) >= 100 else False
                task.save()
            except (Task.DoesNotExist, ValueError):
                continue  # タスクが存在しない場合はスキップ

    return redirect('tasks:task_list')
    
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