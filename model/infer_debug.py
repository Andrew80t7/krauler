# infer_debug.py
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms

from model.neuro_model import VideoClassifier

# from model.neuro_model import load_model

# настройка трансформаций и модели
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def load_model(checkpoint_path: str, num_classes: int = 2, device: torch.device = None):
    """
    Загружает модель VideoClassifier с сохранёнными весами.

    Args:
        checkpoint_path: путь к файлу .pth с state_dict модели.
        num_classes: число выходных классов (по умолчанию 2).
        device: torch.device, куда загрузить модель (cpu или cuda).
                Если None, автоматически выберется CUDA, если доступна.
    Returns:
        model: VideoClassifier в режиме eval.
    """
    device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
    M = VideoClassifier(num_classes=num_classes).to(device)
    state = torch.load(checkpoint_path, map_location=device)
    M.load_state_dict(state)
    M.eval()
    return M


model = load_model('checkpoints/best_model.pth', num_classes=2)


def debug_video(path):
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Всего кадров: {total}")
    indices = np.linspace(0, total - 1, 10, dtype=int)
    print("Индексы:", indices)
    frames = []
    for i in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        print(f"  кадр {i}: {'OK' if ret else 'FAIL'}")
        if ret:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append(transform(img))
    cap.release()
    print(f"Извлечено кадров: {len(frames)}")
    return frames


if __name__ == "__main__":
    debug_video(r"D:\Videos\train\1\IMG_0991.MP4")
