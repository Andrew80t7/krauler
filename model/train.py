# train.py
import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

# относительные импорты внутри пакета model
from .data.download_from_drive import master as download_drive_data
from .dataset import VideoDataset
from .model import VideoClassifier


def main():
    # 1. Подтягиваем видео из Google Drive в локальные data/train/0 и data/train/1
    download_drive_data()

    # 2. Собираем пути и метки, исходя из структуры папок krauler/data/train/{0,1}
    data_root = os.path.join(os.path.dirname(__file__), 'krauler', 'data', 'train')
    video_paths, labels = [], []
    for label_str in ('0', '1'):
        class_dir = os.path.join(data_root, label_str)
        for fname in os.listdir(class_dir):
            if fname.lower().endswith(('.mp4', '.avi', '.mov')):
                video_paths.append(os.path.join(class_dir, fname))
                labels.append(int(label_str))

    # 3. Трансформации (те же, что при обучении)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # 4. Датасет и загрузчик
    dataset = VideoDataset(video_paths, labels, transform=transform, num_frames=10)
    loader = DataLoader(dataset, batch_size=2, shuffle=True, num_workers=4)

    # 5. Модель, оптимизатор, функция потерь
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = VideoClassifier(num_classes=2).to(device)
    optimizer = Adam(model.parameters(), lr=1e-4)
    criterion = CrossEntropyLoss()

    # 6. Цикл обучения
    best_loss = float('inf')
    os.makedirs('checkpoints', exist_ok=True)

    num_epochs = 5
    for epoch in range(1, num_epochs + 1):
        model.train()
        running_loss = 0.0

        for vids, labs in loader:
            vids, labs = vids.to(device), labs.to(device)
            optimizer.zero_grad()
            outputs = model(vids)
            loss = criterion(outputs, labs)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * vids.size(0)

        epoch_loss = running_loss / len(dataset)
        print(f"Epoch {epoch}/{num_epochs} — Loss: {epoch_loss:.4f}")

        # Сохраняем, если улучшилось
        ckpt_path = f'checkpoints/epoch{epoch}.pth'
        torch.save(model.state_dict(), ckpt_path)
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            best_path = 'checkpoints/best_model.pth'
            torch.save(model.state_dict(), best_path)
            print(f"  ↳ New best model saved to {best_path}")

    print("Training complete.")


if __name__ == '__main__':
    main()
