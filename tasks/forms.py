from django import forms
from .models import Task
from django.contrib.auth.forms import AuthenticationForm

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'urgency', 'progress','attachment', 'image', 'is_completed']
        exclude = ['user']  # ユーザーフィールドを除外
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
             'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),  # 追加
           'urgency': forms.Select(attrs={'class': 'form-control'}),  # ウィジェットを追加
        }
        
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment and attachment.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('ファイルサイズは10MB以下にしてください。')
        return attachment

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('画像サイズは10MB以下にしてください。')
        return image
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )