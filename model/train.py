import os
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from dataset import VideoDataset
from model import VideoClassifier
from torch.optim import Adam
from torch.nn import CrossEntropyLoss


def main():
    # Конфигурируем
    data_dir = os.environ['KRAULER_DATA_PATH']
    video_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir)
                   if f.endswith(('.mp4', '.avi', '.mov'))]
    labels = [...]  # ваша разметка

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    dataset = VideoDataset(video_files, labels, transform)
    loader = DataLoader(dataset, batch_size=2, shuffle=True)

    device = torch.device('cuda')
    model = VideoClassifier(num_classes=2).to(device)
    opt = Adam(model.parameters(), lr=1e-4)
    loss_fn = CrossEntropyLoss()

    for epoch in range(5):
        model.train()
        total_loss = 0
        for vids, labs in loader:
            vids, labs = vids.to(device), labs.to(device)
            opt.zero_grad()
            out = model(vids)
            loss = loss_fn(out, labs)
            loss.backward()
            opt.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}: loss={total_loss / len(loader)}")
        torch.save(model.state_dict(), 'checkpoint.pth')


if __name__ == '__main__':
    main()
