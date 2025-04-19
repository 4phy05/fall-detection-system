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

@login_required
def detection_view(request):
    if request.method == 'POST':
        # 确保上传目录存在
        ensure_upload_dir()
        
        detection_type = request.POST.get('detection_type')
        print(f"接收到的检测类型: {detection_type}")
        print(f"POST数据: {request.POST}")
        print(f"FILES数据: {request.FILES}")  # 检查是否收到文件
        
        try:
            if detection_type == 'camera':
                return handle_camera_detection(request)
            elif detection_type == 'video':
                return handle_video_detection(request)
            elif detection_type == 'image':
                return handle_image_detection(request)
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'未知的检测类型：{detection_type}'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'检测失败: {str(e)}'
            })
    
    return render(request, 'detection.html')

@login_required
def handle_camera_detection(request):
    try:
        # 初始化摄像头
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return JsonResponse({
                'success': False,
                'message': '无法访问摄像头'
            })
            
        # 加载YOLO模型
        model = YOLO('app/static/models/best.pt')
        
        # 捕获一帧
        ret, frame = cap.read()
        if not ret:
            return JsonResponse({
                'success': False,
                'message': '无法获取摄像头画面'
            })
            
        # 进行检测
        results = model(frame)
        
        # 生成唯一文件名
        timestamp = str(int(time.time() * 1000))
        result_path = os.path.join(settings.MEDIA_ROOT, 'upload_files', f'camera_{timestamp}.jpg')
        
        # 保存检测结果
        for r in results:
            im_array = r.plot()
            r.save(result_path)
        
        # 释放摄像头
        cap.release()
        
        return JsonResponse({
            'success': True,
            'type': 'camera',
            'message': '摄像头检测完成',
            'result_image': f'/media/upload_files/camera_{timestamp}.jpg'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'摄像头检测出错：{str(e)}'
        })

@login_required
def handle_video_detection(request):
    try:
        video_file = request.FILES.get('file')
        if not video_file:
            return JsonResponse({
                'success': False,
                'message': '请选择视频文件'
            })
            
        # 检查文件类型
        if not video_file.name.lower().endswith(('.mp4', '.avi')):
            return JsonResponse({
                'success': False,
                'message': '请上传 mp4 或 avi 格式的视频'
            })
            
        # 生成唯一文件名
        timestamp = str(int(time.time() * 1000))
        video_path = os.path.join(settings.MEDIA_ROOT, 'upload_files', f'upload_{timestamp}.mp4')
        result_path = os.path.join(settings.MEDIA_ROOT, 'upload_files', f'result_{timestamp}.mp4')
        
        # 保存上传的视频
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
                
        # 加载YOLO模型
        model = YOLO('app/static/models/best.pt')
        
        # 处理视频
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建视频写入器
        out = cv2.VideoWriter(result_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # 进行检测
            results = model(frame)
            detected_frame = results[0].plot()
            out.write(detected_frame)
            
            frame_count += 1
            progress = int((frame_count / total_frames) * 100)
            
        cap.release()
        out.release()
        
        return JsonResponse({
            'success': True,
            'type': 'video',
            'message': '视频检测完成',
            'result_path': f'/media/upload_files/result_{timestamp}.mp4',
            'progress': 100
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'视频处理出错：{str(e)}'
        })

@login_required
def handle_image_detection(request):
    try:
        image_file = request.FILES.get('file')
        if not image_file:
            print("没有接收到文件")  # 调试信息
            return JsonResponse({
                'success': False,
                'message': '请选择图片文件'
            })
            
        print(f"接收到文件：{image_file.name}")  # 调试信息
        
        # 检查文件类型
        if not image_file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return JsonResponse({
                'success': False,
                'message': '请上传 jpg、jpeg 或 png 格式的图片'
            })
            
        # 生成唯一文件名
        timestamp = str(int(time.time() * 1000))
        image_path = os.path.join(settings.MEDIA_ROOT, 'upload_files', f'upload_{timestamp}.jpg')
        
        print(f"准备保存文件到：{image_path}")  # 调试信息
        
        # 确保目录存在
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # 保存上传的图片
        with open(image_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
                
        print(f"文件已保存到：{image_path}")  # 调试信息
        
        # 加载YOLO模型
        model = YOLO('app/static/models/best.pt')
        
        # 进行检测
        results = model(image_path)
        
        # 保存检测结果
        for r in results:
            im_array = r.plot()
            r.save(image_path)
        
        return JsonResponse({
            'success': True,
            'type': 'image',
            'message': '图片检测完成',
            'result_image': f'/media/upload_files/result_{timestamp}.jpg'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'图片处理出错：{str(e)}'
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

@login_required
def get_video_progress(request):
    video_id = request.GET.get('video_id')
    if video_id:
        progress = request.session.get(f'video_progress_{video_id}', 0)
        return JsonResponse({'progress': progress})
    return JsonResponse({'progress': 0})

def ensure_upload_dir():
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'upload_files')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
