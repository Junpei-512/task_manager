from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # 追加
from tasks.views import CustomLoginView, register  # カスタムログインビューをインポート
from django.conf import settings  # 追加
from django.conf.urls.static import static  # 追加


urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    # ルートURLをログインビューに設定
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # ここで追加
    path('register/', register, name='register'),  # 追加
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)