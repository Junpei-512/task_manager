from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Task
from .forms import TaskForm
from django.db.models import Q
from django.contrib.auth import views as auth_views
from .forms import LoginForm

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    
@login_required
def task_list(request):
    # 認証されていない場合はログインページにリダイレクト
    if not request.user.is_authenticated:
        return redirect('login')
    tasks = Task.objects.filter(user=request.user).order_by('due_date')

    query = request.GET.get('q')  # 検索キーワード
    due_date = request.GET.get('due_date')  # 期限フィルタ
    urgency = request.GET.get('urgency')
    tasks = Task.objects.all().order_by('due_date')
    if query:
        tasks = tasks.filter(title__icontains=query)

    if due_date:
        tasks = tasks.filter(due_date=due_date)
        
    if urgency:
         tasks = tasks.filter(urgency=urgency)

   
    # ページネーションの追加
    paginator = Paginator(tasks, 10)  # 1ページあたり10件表示
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tasks/task_list.html', {'tasks': tasks})

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

