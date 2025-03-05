from ultralytics import YOLO

# 加载预训练模型
model = YOLO("yolov9t.pt")

if __name__ == "__main__":
    # 训练模型
    results = model.train(
        data="datasets/FallData/data.yaml",
        epochs=150,
        batch=10,
        device="cpu",
        save=True,
        save_period=20,
        name="model",
        exist_ok=True
    )
    # 评估模型
    value_results = model.val()