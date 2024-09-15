from django import forms
from django.conf import settings
from .models import Task
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'urgency', 'progress','attachment', 'image', 'is_completed', 'parent', 'related_task']
        exclude = ['user']  # ユーザーフィールドを除外
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
             'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),  # 追加
           'urgency': forms.Select(attrs={'class': 'form-control'}),  # ウィジェットを追加
           'parent': forms.Select(attrs={'class': 'form-control'}),
           'related_task': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment and attachment.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(_('ファイルサイズは10MB以下にしてください。'))
        return attachment

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(_('画像サイズは10MB以下にしてください。'))
        return image
        
    def register(request):
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, _('アカウントが作成されました。'))
                return redirect('tasks:task_list')
        else:
            form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
        
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_('email'))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
