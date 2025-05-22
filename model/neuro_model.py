# krauler/neuro_model.py
import torch
from torchvision import models
from torch.nn import LSTM, Linear, Flatten, Sequential


class VideoClassifier(torch.nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        backbone = models.resnet18(
            weights=models.ResNet18_Weights.IMAGENET1K_V1
        )
        self.feature_extractor = Sequential(
            *list(backbone.children())[:-1],
            Flatten()
        )
        self.lstm = LSTM(512, 256, batch_first=True)
        self.classifier = Linear(256, num_classes)

    def forward(self, x):
        b, t, c, h, w = x.shape
        x = x.view(-1, c, h, w)
        features = self.feature_extractor(x).view(b, t, -1)
        lstm_out, _ = self.lstm(features)
        return self.classifier(lstm_out[:, -1, :])


def predict_video(video_path, model, transform, device=None, num_frames=10):
    import cv2
    from PIL import Image
    import numpy as np
    import torch

    device = device or next(model.parameters()).device

    try:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise RuntimeError(f'Cannot open video {video_path}')

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        if total <= 0 or total < num_frames:
            return -1

        indices = np.linspace(0, total - 1, 10, dtype=int)

        frames = []
        cap = cv2.VideoCapture(video_path)
        for i in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                continue
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frames.append(transform(img))

        cap.release()
        if len(frames) < 10:
            return -1

        batch = torch.stack(frames).unsqueeze(0).to(device)
        with torch.no_grad():
            out = model(batch)
            return int(out.argmax(1))

    except Exception as e:
        print(f"[WARN] cannot infer {video_path!r}: {e}")
        return -1