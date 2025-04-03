from ultralytics import YOLO

# 加载预训练的YOLOv9模型
model = YOLO("/kaggle/input/yolov9c/pytorch/default/1/yolov9c.pt")

# 开始训练
model.train(
    data="/kaggle/input/fall-detection/datasets/data.yaml",        # 数据集配置文件路径
    epochs=100,              # 总训练轮数
    batch=32,                # 批次大小，根据GPU内存适当调整
    imgsz=640,               # 输入图像尺寸
    device="0,1",            # 使用Kaggle提供的两块T4 GPU
    workers=8,               # 数据加载线程数
    optimizer="AdamW",       # 优化器，可选SGD、Adam、AdamW
    lr0=0.001,               # 初始学习率
    weight_decay=0.0005,     # 权重衰减
    patience=20,             # 早停轮数
    project="runs/train",    # 训练结果保存路径
    name="yolov9_custom",    # 训练任务名称
    exist_ok=True,           # 是否覆盖已有的训练结果
    amp=True,                # 使用自动混合精度训练
    freeze=10,               # 冻结前10层以加速收敛
    hsv_h=0.015,             # 色调变化
    hsv_s=0.7,               # 饱和度变化
    hsv_v=0.4,               # 明度变化
    degrees=0.5,             # 随机旋转角度
    translate=0.1,           # 平移
    scale=0.5,               # 缩放
    shear=0.1,               # 剪切
    perspective=0.0005,      # 透视变换
    flipud=0.0,              # 上下翻转
    fliplr=0.5,              # 左右翻转
    mosaic=1.0,              # Mosaic数据增强
    mixup=0.2,               # MixUp数据增强
)
