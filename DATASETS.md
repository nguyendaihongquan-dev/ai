# 📚 Dataset và Repo GitHub cho Video Sentiment/Emotion Classification

Tài liệu này tổng hợp các dataset và repository GitHub liên quan đến phân loại cảm xúc/tích cực-tiêu cực trong video.

## 🎯 Dataset Chính

### 1. **Video-Sentiment-Analysis** (GitHub)
- **Link**: https://github.com/Nirmalvekariya/Video-Sentiment-Analysis
- **Mô tả**: Dự án phân tích cảm xúc video bằng Deep Learning với độ chính xác 72%
- **Tính năng**: 
  - Cho phép upload hoặc quay video để phân tích
  - Sử dụng mô hình nhận diện cảm xúc dựa trên học sâu
- **Có thể clone và sử dụng code**

### 2. **Multimodal-Sentiment-Analysis**
- **Link**: https://git.hubp.de/soujanyaporia/multimodal-sentiment-analysis
- **Mô tả**: Phân tích cảm xúc đa phương thức, kết hợp hình ảnh, âm thanh, văn bản
- **Tính năng**: Hợp nhất thông tin từ nhiều kênh để phân tích cảm xúc

### 3. **VEATIC Dataset**
- **Link**: https://arxiv.org/abs/2309.06745
- **Mô tả**: Dataset lớn với 124 video từ phim Hollywood, tài liệu, video gia đình
- **Đặc điểm**:
  - Được gán nhãn liên tục về mức độ cảm xúc (valence và arousal)
  - Mỗi frame có đánh giá cảm xúc
- **Có thể download từ arXiv hoặc trang chủ dataset**

### 4. **Video Dataset for Sentiment Analysis** (Mendeley)
- **Link**: https://data.mendeley.com/datasets/jrvj6rpnjd/1
- **Mô tả**: 600 video từ các nền tảng mạng xã hội
- **Nhãn**: 
  - Sợ hãi (Fear)
  - Buồn bã (Sad)
  - Tức giận (Anger)
  - Ghê tởm (Disgust)
  - Trung lập (Neutral)
  - Hạnh phúc (Happy)
  - Ngạc nhiên (Surprise)
- **Có thể download trực tiếp từ Mendeley Data**

## 🔍 Dataset Khác

### 5. **FER2013** (Face Emotion Recognition)
- **Mô tả**: Dataset về nhận diện cảm xúc trên khuôn mặt
- **Lưu ý**: Chủ yếu là ảnh, không phải video, nhưng có thể extract frames từ video

### 6. **AffectNet**
- **Mô tả**: Dataset lớn về cảm xúc với hơn 1 triệu ảnh
- **Có thể sử dụng**: Extract frames từ video và sử dụng nhãn cảm xúc

## 🛠️ Cách Sử dụng

### Option 1: Tải dataset từ Mendeley
```bash
# Dataset 600 videos với 7 cảm xúc
# Link: https://data.mendeley.com/datasets/jrvj6rpnjd/1
# Cần đăng ký tài khoản Mendeley để download
```

### Option 2: Clone repo và sử dụng code
```bash
# Clone Video-Sentiment-Analysis
git clone https://github.com/Nirmalvekariya/Video-Sentiment-Analysis.git
cd Video-Sentiment-Analysis
```

### Option 3: Tạo dataset từ YouTube
- Sử dụng script tải video từ YouTube
- Tự gán nhãn positive/negative
- Sử dụng cho fine-tune model

## 📝 Gợi ý cho Dự án

### Dataset Positive/Negative đơn giản:
1. **Tải video từ YouTube Shorts**:
   - Positive: Tìm video vui, hạnh phúc, tích cực
   - Negative: Tìm video buồn, tiêu cực, tức giận

2. **Sử dụng script có sẵn**:
   ```bash
   # Tạo cấu trúc dataset
   python setup_dataset.py
   
   # Tải video và đặt vào thư mục tương ứng
   # dataset/positive/ và dataset/negative/
   ```

3. **Fine-tune model**:
   ```bash
   python videomae_finetune.py
   ```

## 🔗 Tài nguyên Bổ sung

- **HuggingFace Datasets**: Tìm kiếm "video emotion" hoặc "video sentiment"
- **Kaggle**: Có nhiều dataset về video emotion classification
- **Papers with Code**: Xem các dataset được sử dụng trong research papers

## ⚠️ Lưu ý

1. **Bản quyền**: Kiểm tra license của dataset trước khi sử dụng
2. **Kích thước**: Một số dataset rất lớn, cần đủ dung lượng ổ cứng
3. **Format**: Có thể cần convert format video để phù hợp với model
4. **Nhãn**: Một số dataset có nhiều nhãn cảm xúc, cần map về positive/negative

## 🚀 Bước Tiếp theo

1. Chọn dataset phù hợp với nhu cầu
2. Download và tổ chức dataset theo cấu trúc:
   ```
   dataset/
   ├── positive/
   │   ├── video1.mp4
   │   └── ...
   └── negative/
       ├── video1.mp4
       └── ...
   ```
3. Chạy fine-tune với `videomae_finetune.py`
4. Test với model đã fine-tune

