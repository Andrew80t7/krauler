# krauler/dataset.py
import os
import cv2
import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset


class VideoDataset(Dataset):
    def __init__(self, video_paths, labels=None, transform=None, num_frames=10):
        self.video_paths = video_paths
        self.labels = labels or [0] * len(video_paths)
        self.transform = transform
        self.num_frames = num_frames

    def __len__(self):
        return len(self.video_paths)

    def __getitem__(self, idx):
        path = self.video_paths[idx]
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        indices = np.linspace(0, total - 1, self.num_frames, dtype=int)
        frames = []
        for i in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frm = cap.read()
            if not ret:
                continue
            img = Image.fromarray(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
            frames.append(self.transform(img) if self.transform else img)
        cap.release()
        if not frames:
            # возвращаем «пустой» батч и метку −1
            return torch.zeros(self.num_frames, 3, 224, 224), -1
        return torch.stack(frames), self.labels[idx]
