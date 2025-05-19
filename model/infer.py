import os
import torch
from torchvision import transforms

from model.infer_debug import load_model
from model.neuro_model import predict_video


def main():
    # Путь к файлу с весами (best_model.pth)
    ckpt_path = os.path.join(os.path.dirname(__file__), 'checkpoints', 'best_model.pth')

    # Загружаем модель
    model = load_model(ckpt_path, num_classes=2)

    # Трансформации (должны совпадать с train.py)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # Укажите путь к вашему тестовому видео на диске D:
    test_video = r"D:\Videos\train\1\IMG_0991.MP4"

    # Предсказание: 1 → скачать, 0 → не скачивать, -1 → пропуск
    pred = predict_video(test_video, model, transform)
    if pred == 1:
        result = "Скачать"
    elif pred == 0:
        result = "Не скачивать"
    else:
        result = "Пропустить (битый или неполный файл)"

    print(f"{os.path.basename(test_video)} → {result}")


if __name__ == '__main__':
    main()
