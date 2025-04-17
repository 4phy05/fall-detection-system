from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SimpleUserCreationForm, LoginForm
from .models import CustomUser
import os
from ultralytics import YOLO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import shutil
from django.conf import settings
import time
import cv2

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

def detection_view(request):
    # 检查用户是否已登录
    if not request.user.is_authenticated:
        messages.warning(request, '请先登录后再进行检测！')
        return render(request, 'detection_login_required.html')
    return render(request, 'detection.html')

@login_required
@csrf_exempt
def detect(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            # 创建上传文件目录
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'upload_files')
            os.makedirs(upload_dir, exist_ok=True)

            # 清理之前的文件
            clean_directory(upload_dir)

            # 获取上传的文件
            uploaded_file = request.FILES['file']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            # 生成唯一文件名
            timestamp = int(time.time())
            filename = f"upload_{timestamp}{file_extension}"
            file_path = os.path.join(upload_dir, filename)

            # 保存上传的文件
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # 判断文件类型
            is_video = file_extension in ['.mp4', '.avi']
            
            if is_video:
                # 视频处理
                model = YOLO('app/static/models/best.pt')
                # 创建结果视频目录
                result_filename = f"result_{timestamp}{file_extension}"
                result_path = os.path.join(upload_dir, result_filename)
                
                # 使用YOLO处理视频
                results = model(file_path, stream=True)  # 流式处理
                
                # 获取视频信息
                cap = cv2.VideoCapture(file_path)
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()

                # 创建视频写入器
                out = cv2.VideoWriter(
                    result_path,
                    cv2.VideoWriter_fourcc(*'mp4v'),
                    fps,
                    (width, height)
                )

                # 处理每一帧
                frame_count = 0
                for r in results:
                    frame_count += 1
                    # 绘制检测框
                    im_array = r.plot()
                    # 写入帧
                    out.write(im_array)
                    
                    # 每处理10帧发送一次进度更新
                    if frame_count % 10 == 0:
                        progress = {
                            'type': 'video',
                            'frame': frame_count,
                            'status': 'processing'
                        }
                        return JsonResponse(progress)

                # 释放视频写入器
                out.release()
                
                # 处理完成，返回结果视频路径
                return JsonResponse({
                    'success': True,
                    'type': 'video',
                    'message': '视频检测完成',
                    'result_path': f"/media/upload_files/{result_filename}",
                    'status': 'completed'
                })
            else:
                # 图片处理（保持原有逻辑）
                model = YOLO('app/static/models/best.pt')
                results = model(file_path)
                
                result_filename = f"result_{timestamp}{file_extension}"
                result_path = os.path.join(upload_dir, result_filename)
                
                for r in results:
                    im_array = r.plot()
                    r.save(result_path)

                return JsonResponse({
                    'success': True,
                    'type': 'image',
                    'message': '图片检测完成',
                    'result_image': f"/media/upload_files/{result_filename}"
                })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'检测失败: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': '请上传有效的文件'
    })

def clean_directory(directory):
    """清理指定目录中的所有文件"""
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Error deleting {file_path}: {str(e)}')
    except Exception as e:
        print(f'Error cleaning directory {directory}: {str(e)}')
