# Hướng dẫn đẩy Docker Image lên Docker Hub

Hướng dẫn chi tiết để đẩy image `videomae-service` lên Docker Hub và chia sẻ với người khác.

## 📋 Yêu cầu

- Docker Desktop đã được cài đặt và đang chạy
- Tài khoản Docker Hub (miễn phí tại https://hub.docker.com/)

## 🔐 Bước 1: Tạo tài khoản Docker Hub (nếu chưa có)

1. Truy cập https://hub.docker.com/
2. Click "Sign Up" và tạo tài khoản miễn phí
3. Xác nhận email nếu được yêu cầu

## 🔑 Bước 2: Đăng nhập Docker Hub

Mở PowerShell hoặc Terminal và chạy:

```powershell
docker login
```

Nhập:
- **Username**: Tên đăng nhập Docker Hub của bạn
- **Password**: Mật khẩu Docker Hub (hoặc Access Token nếu bật 2FA)

Khi thành công, bạn sẽ thấy: `Login Succeeded`

## 🏷️ Bước 3: Tag Image đúng format

Image trên Docker Hub cần có format: `username/repository-name:tag`

**Lưu ý quan trọng**: Thay `YOUR_USERNAME` bằng username Docker Hub thực tế của bạn!

```powershell
# Tag image với username của bạn
docker tag videomae-service YOUR_USERNAME/videomae-service:latest

# Hoặc tag với version cụ thể
docker tag videomae-service YOUR_USERNAME/videomae-service:v1.0.0
```

**Ví dụ** (nếu username là `johndoe`):
```powershell
docker tag videomae-service johndoe/videomae-service:latest
```

## 📤 Bước 4: Push Image lên Docker Hub

```powershell
# Push image latest
docker push YOUR_USERNAME/videomae-service:latest

# Hoặc push version cụ thể
docker push YOUR_USERNAME/videomae-service:v1.0.0
```

**Ví dụ**:
```powershell
docker push johndoe/videomae-service:latest
```

Quá trình push có thể mất vài phút tùy vào kích thước image và tốc độ mạng.

## ❌ Xử lý lỗi "push access denied"

Nếu gặp lỗi `push access denied, repository does not exist or may require authorization`, kiểm tra:

1. **Đã đăng nhập chưa?**
   ```powershell
   docker login
   ```

2. **Username trong tag có đúng không?**
   - Kiểm tra username Docker Hub tại https://hub.docker.com/settings/account
   - Đảm bảo tag có format: `username/videomae-service:tag`

3. **Repository đã tồn tại trên Docker Hub?**
   - Docker Hub tự động tạo repository khi push lần đầu
   - Đảm bảo repository name không vi phạm quy tắc đặt tên

4. **Kiểm tra quyền truy cập:**
   ```powershell
   docker logout
   docker login
   ```

## 📥 Bước 5: Người khác pull và sử dụng

Sau khi push thành công, người khác có thể sử dụng image:

### Pull image

```powershell
docker pull YOUR_USERNAME/videomae-service:latest
```

### Chạy container

**Windows (PowerShell):**
```powershell
docker run -d --name videomae-api -p 8000:8000 `
  -v C:\path\to\videomae_finetuned_final:/models/videomae_finetuned_final `
  YOUR_USERNAME/videomae-service:latest
```

**Linux/Mac:**
```bash
docker run -d --name videomae-api -p 8000:8000 \
  -v /path/to/videomae_finetuned_final:/models/videomae_finetuned_final \
  YOUR_USERNAME/videomae-service:latest
```

### Test API

```powershell
# Health check
curl.exe http://localhost:8000/health

# Predict với file upload
curl.exe -X POST http://localhost:8000/predict `
  -F "video_file=@path/to/video.mp4;type=video/mp4"
```

## 📝 Lưu ý quan trọng

### Model Weights không có trong image

- Image `videomae-service` **KHÔNG chứa** model weights để giảm kích thước
- Người dùng **PHẢI** mount thư mục `videomae_finetuned_final` khi chạy container
- Đảm bảo thư mục model có đầy đủ file: `config.json`, `model.safetensors`, `preprocessor_config.json`, v.v.

### Nếu muốn đóng gói model vào image

Nếu muốn tạo image có sẵn model (image sẽ rất lớn, ~2-5GB):

1. Tạo `Dockerfile.with-model`:
```dockerfile
FROM videomae-service:latest
COPY videomae_finetuned_final /models/videomae_finetuned_final
ENV VIDEOMAE_MODEL_PATH=/models/videomae_finetuned_final
```

2. Build và push:
```powershell
docker build -f Dockerfile.with-model -t YOUR_USERNAME/videomae-service:with-model .
docker push YOUR_USERNAME/videomae-service:with-model
```

## 🚀 Sử dụng script tự động

Thay vì chạy từng lệnh, bạn có thể dùng script `docker-push.ps1`:

```powershell
.\docker-push.ps1 -Username YOUR_USERNAME -Tag latest
```

Xem chi tiết trong file `docker-push.ps1`.

## 📚 Tài liệu tham khảo

- Docker Hub: https://hub.docker.com/
- Docker Documentation: https://docs.docker.com/
- Docker CLI Reference: https://docs.docker.com/reference/cli/

