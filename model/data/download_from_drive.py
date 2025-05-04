from pathlib import Path
import gdown

# Словарь метка → ID папки на Google Drive
DRIVE_FOLDERS = {
    "0": "ВАШ_FOLDER_ID_0",
    "1": "ВАШ_FOLDER_ID_1",
}


def download_folder_from_drive(folder_id: str, output_dir: Path):
    """
    Скачивает все файлы из папки Google Drive (рекурсивно)
    в локальную директорию output_dir.
    """
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    gdown.download_folder(url, output=str(output_dir), quiet=False, use_cookies=False)


def master():
    base = Path(__file__).parent.parent / "data" / "train"
    for label, folder_id in DRIVE_FOLDERS.items():
        out_dir = base / label
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"Скачиваю класс {label} → {out_dir}")
        download_folder_from_drive(folder_id, out_dir)

    print("Загрузка завершена!")


if __name__ == "__main__":
    master()
