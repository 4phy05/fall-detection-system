from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SimpleUserCreationForm, LoginForm
from .models import CustomUser  # 导入自定义用户模型

# 首页
def index(request):
    return render(request, 'index.html')

# 注册
def register(request):
    if request.method == 'POST':
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 添加成功消息
            messages.success(request, '注册成功！请登录您的账号。')
            return redirect('login')
    else:
        form = SimpleUserCreationForm()
    return render(request, 'register.html', {'form': form})

# 登录
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            
            # 先检查用户是否存在
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                messages.error(request, '用户不存在！')
                return render(request, "login.html", {"form": form})
            
            # 验证密码
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '登录成功！')
                return redirect('index')
            else:
                messages.error(request, '密码错误！')
                return render(request, "login.html", {"form": form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {"form": form})

# 退出登录
@login_required
def user_logout(request):
    logout(request)
    return redirect('index')
