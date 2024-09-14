from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'tasks'  # 名前空間を追加

urlpatterns = [
    path('list/', views.task_list, name='task_list'),
    path('update_progress/', views.update_progress, name='update_progress'),  # 追加
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/new/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
