import os
import cv2
import numpy as np
import torch
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset


class VideoDataset(Dataset):
    """
    Dataset for loading video files stored locally.

    Параметры:
        root_dir: Path или str к корневой папке с подпапками классов (например, '0', '1')
        labels_map: dict, отображающий имя подпапки в метку (по умолчанию {'0':0, '1':1})
        transform: torchvision.transforms для обработки кадров
        num_frames: int, число кадров на видео
    """

    def __init__(self, root_dir, labels_map=None, transform=None, num_frames=10):
        self.root_dir = Path(root_dir)
        self.labels_map = labels_map or {'0': 0, '1': 1}
        self.transform = transform
        self.num_frames = num_frames

        # Собираем все (video_path, label)
        self.samples = []
        for subfolder, label in self.labels_map.items():
            folder = self.root_dir / subfolder
            if not folder.exists():
                continue
            for fname in os.listdir(folder):
                if fname.lower().endswith(('.mp4', '.avi', '.mov')):
                    self.samples.append((folder / fname, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        video_path, label = self.samples[idx]
        cap = cv2.VideoCapture(str(video_path))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        indices = np.linspace(0, total - 1, self.num_frames, dtype=int)

        frames = []
        for i in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                continue
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if self.transform:
                img = self.transform(img)
            frames.append(img)
        cap.release()

        if not frames:
            # Возвращаем "пустой" тензор и метку -1
            empty = torch.zeros((self.num_frames, 3, 224, 224))
            return empty, -1

        video_tensor = torch.stack(frames)
        return video_tensor, label
