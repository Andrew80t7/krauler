import os
import cv2
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

from model.dataset import VideoDataset
from model.neuro_model import VideoClassifier

# Количество кадров на видео, размер батча и число эпох
NUM_FRAMES = 10
BATCH_SIZE = 2
NUM_EPOCHS = 5

def collate_fn(batch):
    """
    Собирает батч, отфильтровывая неполные или битые примеры.
    """
    vids_list, labs_list = [], []
    for vid, lab in batch:
        # проверяем, что тензор валиден и содержит ровно NUM_FRAMES
        if isinstance(vid, torch.Tensor) and vid.ndim == 4 and vid.size(0) == NUM_FRAMES and lab >= 0:
            vids_list.append(vid)
            labs_list.append(lab)
    if not vids_list:
        return torch.empty(0), torch.empty(0, dtype=torch.long)
    vids = torch.stack(vids_list, dim=0)
    labs = torch.tensor(labs_list, dtype=torch.long)
    return vids, labs

def filter_samples(dataset):
    """
    Удаляет из dataset.samples видео с общей длиной кадров < NUM_FRAMES
    или не открывающиеся вовсе.
    """
    valid = []
    for path, lab in dataset.samples:
        cap = cv2.VideoCapture(str(path))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        if total >= NUM_FRAMES:
            valid.append((path, lab))
    dataset.samples = valid

def main():
    # Путь к папкам с обучающим датасетом (0/ и 1/)
    data_root = r"D:\Videos\train"

    # Трансформации кадров
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # Создание датасета и фильтрация битых видео
    dataset = VideoDataset(
        root_dir=data_root,
        transform=transform,
        num_frames=NUM_FRAMES
    )
    filter_samples(dataset)
    if len(dataset) == 0:
        print("No valid videos found. Exiting.")
        return

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        collate_fn=collate_fn
    )

    # Модель, оптимизатор, функция потерь
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = VideoClassifier(num_classes=2).to(device)
    optimizer = Adam(model.parameters(), lr=1e-4)
    criterion = CrossEntropyLoss()

    os.makedirs('checkpoints', exist_ok=True)
    best_loss = float('inf')

    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        running_loss = 0.0
        total_samples = 0

        for vids, labs in loader:
            if vids.numel() == 0:
                continue

            vids, labs = vids.to(device), labs.to(device)
            optimizer.zero_grad()
            outputs = model(vids)
            loss = criterion(outputs, labs)
            loss.backward()
            optimizer.step()

            bs = vids.size(0)
            running_loss += loss.item() * bs
            total_samples += bs

        if total_samples == 0:
            print(f"Epoch {epoch}: no valid samples, stopping.")
            break

        epoch_loss = running_loss / total_samples
        print(f"Epoch {epoch}/{NUM_EPOCHS} — Loss: {epoch_loss:.4f}")

        if epoch_loss < best_loss:
            best_loss = epoch_loss
            torch.save(model.state_dict(), 'checkpoints/best_model.pth')
            print(f"  ↳ New best model saved (loss={best_loss:.4f})")

    print("Training complete.")

if __name__ == '__main__':
    main()
