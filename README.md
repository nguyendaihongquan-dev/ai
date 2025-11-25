# VideoMAE - Phân loại Video Tích cực/Tiêu cực

Dự án sử dụng VideoMAE để phân loại cảm xúc tích cực/tiêu cực trong video.

## 📋 Yêu cầu

- Python 3.9 - 3.11
- pip

## 🚀 Cài đặt

### Bước 1: Cài đặt môi trường

**Cho máy thường (Windows/Linux/Intel Mac):**
```bash
pip install -r requirements.txt
```

**Cho Mac M1/M2/M3:**
```bash
pip install transformers accelerate av decord numpy pillow
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Bước 2: Test model cơ bản

Đặt file video tên `demo.mp4` trong thư mục gốc và chạy:

```bash
python videomae_test.py
```

Hoặc chỉ định đường dẫn video:
```bash
python videomae_test.py path/to/your/video.mp4
```

## 📁 Cấu trúc dự án

```
.
├── requirements.txt          # Danh sách thư viện cần thiết
├── extract_frames.py        # Script trích xuất frames từ video
├── videomae_test.py         # Script test model VideoMAE gốc
├── videomae_finetune.py     # Script fine-tune model cho positive/negative
├── videomae_predict.py      # Script dự đoán với model đã fine-tune
├── download_youtube_dataset.py  # Script tải video từ YouTube
├── DATASETS.md              # Danh sách dataset và tài nguyên
├── .gitignore               # Git ignore file
└── README.md                # File hướng dẫn này
```

## ⚠️ Lưu ý

Model VideoMAE gốc (`MCG-NJU/videomae-base-finetuned-kinetics-400`) được train trên dataset Kinetics-400 (hành động), không phải cảm xúc. 

Để phân loại **tích cực/tiêu cực**, bạn cần:
1. Chuẩn bị dataset với nhãn positive/negative
2. Fine-tune model bằng script `videomae_finetune.py`

## 🔧 Fine-tune Model

### Bước 1: Chuẩn bị Dataset

Tạo cấu trúc thư mục dataset tự động:
```bash
python setup_dataset.py
```

Hoặc tạo thủ công:
```bash
mkdir -p dataset/positive dataset/negative
```

Đặt các video tích cực vào `dataset/positive/` và video tiêu cực vào `dataset/negative/`

### Bước 2: Chạy Fine-tune

```bash
python videomae_finetune.py
```

Model đã fine-tune sẽ được lưu tại `./videomae_finetuned_final`

### Bước 3: Test Model đã Fine-tune

```bash
python videomae_predict.py path/to/video.mp4
```

## 🐳 Chạy Backend bằng Docker

### Build image
```
docker build -t videomae-service .
```

### Run container
Mount thư mục chứa model đã fine-tune vào `/models` (đảm bảo có `videomae_finetuned_final` bên trong):
```
docker run -it --rm -p 8000:8000 ^
  -v C:\Users\BKFET-D8707-KieN\Desktop\ai\videomae_finetuned_final:/models/videomae_finetuned_final ^
  videomae-service
```

API sẽ sẵn sàng tại `http://localhost:8000`. Gửi request:
```
curl -X POST http://localhost:8000/predict ^
  -F "video_url=https://example.com/video.mp4"
```

## 📝 Dataset Format

Dataset cần có cấu trúc:
```
dataset/
├── positive/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
└── negative/
    ├── video1.mp4
    ├── video2.mp4
    └── ...
```

## 📚 Dataset và Tài nguyên

### Tải Dataset từ GitHub/Online

Xem file `DATASETS.md` để biết danh sách các dataset có sẵn:
- Video-Sentiment-Analysis (GitHub)
- VEATIC Dataset (124 videos)
- Video Dataset for Sentiment Analysis (600 videos từ Mendeley)
- Và nhiều dataset khác

### Tạo Dataset từ YouTube

Sử dụng script `download_youtube_dataset.py` để tải video từ YouTube:

```bash
# Tải một video
python download_youtube_dataset.py <youtube_url> <positive|negative>

# Tải nhiều video từ file
python download_youtube_dataset.py --file urls.txt
```

File `urls.txt` format:
```
https://youtube.com/watch?v=xxx1,positive
https://youtube.com/watch?v=xxx2,negative
https://youtube.com/shorts/xxx3,positive
```

