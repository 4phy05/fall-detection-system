from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # 导入自定义用户模型

class SimpleUserCreationForm(UserCreationForm):
    # 覆盖密码字段，移除验证
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请再次输入密码'
        })
    )

    class Meta:
        model = CustomUser  # 使用自定义用户模型
        fields = ('username', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 移除密码复杂度验证提示
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        # 自定义字段标签
        self.fields['username'].label = '用户名'
        # 自定义错误信息
        self.fields['username'].error_messages = {'unique': '该用户名已被使用'}
        self.fields['password2'].error_messages = {'password_mismatch': '两次输入的密码不匹配'}

    def clean_password2(self):
        # 只验证两次密码是否一致，不做其他验证
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.fields['password2'].error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

class LoginForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )
