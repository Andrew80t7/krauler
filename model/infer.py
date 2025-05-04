import os
from torchvision import transforms
from model import load_model, predict_video

if __name__ == '__main__':
    model = load_model('checkpoint.pth', num_classes=2)
    transform = transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    path = '/path/to/some_video.mp4'
    pred = predict_video(path, model, transform)
    print('Скачать' if pred==1 else 'Не скачивать')
