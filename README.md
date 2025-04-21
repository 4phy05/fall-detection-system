### 基于 YOLOv9 的跌倒检测系统
#### 一、实现功能
- 摄像头检测
- 视频检测
- 图像检测
#### 二、模型选择
预训练模型为 yolov9t.pt ，经过训练之后实现检测功能。为了提升实现的摄像头检测的实时性，采用了小参数模型，在实现不错的准确性的前提下，提升模型的检测速度
#### 三、数据集介绍
数据集总数为 11,063 张图片，配比为 train:val:test=7:1:2
#### 四、训练平台
训练平台采用 kaggle 训练平台
#### 五、训练效果
- `labels_correlogram.jpg`
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\labels_correlogram.jpg "labels_correlogram.jpg")
- `labels.jpg`
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\labels.jpg "labels.jpg")
- `F1_curve.png`
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system/app/static/images/F1_curve.png "F1_curve.png")
- `P_curve.png`
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\P_curve.png "P_curve.png")
- `R_curve.png`
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\R_curve.png "R_curve.png")
- `results.png`
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\results.png "results.png")
#### 六、项目结构
`本项目采用 Django 框架搭建 web 框架`

主要目录结构
 - fall_detection_system
    - app
        - static（存放网页静态内容）
        - templates（存放网页代码）
        - views.py（视图函数实现）
        - model.py（用户结构定义）
    - fall_detection_system
        - urls.py（路由定义）
    - manage.py（启动项目文件）
#### 七、项目界面演示
- 首页界面
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\index_1.png "index_1.png")
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\index_2.png "index_2.png")
- 登录界面
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\login.png "login.png")
- 注册界面
![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\sign_in.png "sign_in.png")
- 检测界面
    - 图像检测
    ![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\image_detection.png "image_detection.png")
    - 视频检测
    ![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\video_detection.png "video_detection.png")
    - 摄像头检测
    ![image](https://github.com/4phy05/graduation_project/blob/master/fall_detection_system\app\static\images\camera_detection.png "camera_detection.png")