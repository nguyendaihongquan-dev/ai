"""
Script tự động tải dataset video positive/negative từ YouTube
"""
import os
import subprocess
import time
from pathlib import Path
import random

def check_yt_dlp():
    """Kiểm tra yt-dlp"""
    try:
        subprocess.run(["python3", "-m", "yt_dlp", "--version"], 
                      capture_output=True, check=True)
        return True
    except:
        return False

def install_yt_dlp():
    """Cài đặt yt-dlp"""
    print("Đang cài đặt yt-dlp...")
    subprocess.run(["python3", "-m", "pip", "install", "yt-dlp", "--quiet"])
    print("✓ Đã cài đặt yt-dlp")

def search_and_download(query, output_dir, max_results=10, label=""):
    """Tìm kiếm và tải video từ YouTube"""
    print(f"\n🔍 Đang tìm kiếm: '{query}' ({label})")
    
    # Tạo URL tìm kiếm YouTube
    search_url = f"ytsearch{max_results}:{query}"
    
    # Lấy danh sách video
    cmd = [
        "python3", "-m", "yt_dlp",
        "--flat-playlist",
        "--print", "%(id)s|%(title)s",
        search_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ⚠️  Không tìm thấy video cho: {query}")
            return 0
        
        lines = result.stdout.strip().split('\n')
        downloaded = 0
        
        for line in lines:
            if '|' not in line:
                continue
            
            video_id, title = line.split('|', 1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Tạo tên file an toàn
            safe_title = "".join(c for c in title[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            output_path = output_dir / f"{label}_{downloaded + 1:03d}_{safe_title}.mp4"
            
            # Bỏ qua nếu file đã tồn tại
            if output_path.exists():
                print(f"  ⏭️  Đã tồn tại: {title[:50]}")
                continue
            
            print(f"  📥 Đang tải: {title[:60]}")
            
            # Tải video
            download_cmd = [
                "python3", "-m", "yt_dlp",
                "-f", "best[ext=mp4][height<=720]",  # Chất lượng vừa phải
                "--no-playlist",
                "-o", str(output_path),
                video_url
            ]
            
            try:
                result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0 and output_path.exists():
                    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                    print(f"  ✓ Đã tải: {title[:50]} ({file_size:.1f}MB)")
                    downloaded += 1
                    time.sleep(2)  # Tránh rate limit
                else:
                    print(f"  ❌ Lỗi khi tải: {title[:50]}")
            except subprocess.TimeoutExpired:
                print(f"  ⏱️  Timeout: {title[:50]}")
            except Exception as e:
                print(f"  ❌ Lỗi: {e}")
        
        return downloaded
    
    except Exception as e:
        print(f"  ❌ Lỗi khi tìm kiếm: {e}")
        return 0

def main():
    print("=" * 70)
    print("AUTO DOWNLOAD VIDEO DATASET FROM YOUTUBE")
    print("=" * 70)
    
    # Kiểm tra yt-dlp
    if not check_yt_dlp():
        install_yt_dlp()
    
    # Tạo cấu trúc dataset
    base_dir = Path("dataset")
    positive_dir = base_dir / "positive"
    negative_dir = base_dir / "negative"
    
    positive_dir.mkdir(parents=True, exist_ok=True)
    negative_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✓ Đã tạo cấu trúc dataset:")
    print(f"  - Positive: {positive_dir}")
    print(f"  - Negative: {negative_dir}")
    
    # Từ khóa tìm kiếm cho positive videos
    positive_keywords = [
        "happy people laughing",
        "joy celebration",
        "smiling children",
        "positive motivation",
        "success achievement",
        "funny moments",
        "dancing happy",
        "celebration party",
        "love happiness",
        "success story"
    ]
    
    # Từ khóa tìm kiếm cho negative videos
    negative_keywords = [
        "sad crying",
        "anger frustration",
        "depression sadness",
        "disappointment",
        "fear anxiety",
        "sad story",
        "emotional pain",
        "loneliness",
        "stress worry",
        "negative emotions"
    ]
    
    print("\n" + "=" * 70)
    print("BẮT ĐẦU TẢI DATASET")
    print("=" * 70)
    
    # Lấy số lượng video từ tham số hoặc dùng mặc định
    import sys
    if len(sys.argv) > 1:
        try:
            num_videos = int(sys.argv[1])
        except:
            num_videos = 10
    else:
        num_videos = 10  # Mặc định 10 videos mỗi loại
    
    videos_per_keyword = max(1, num_videos // len(positive_keywords))
    
    print(f"\n📊 Sẽ tải khoảng {num_videos} videos mỗi loại")
    print(f"   ({videos_per_keyword} videos cho mỗi từ khóa)")
    print("\n⚠️  Lưu ý: Quá trình này có thể mất vài phút đến vài giờ")
    print("   tùy thuộc vào số lượng video và tốc độ mạng")
    print(f"\n🚀 Bắt đầu tải...")
    
    # Tải positive videos
    print("\n" + "=" * 70)
    print("TẢI POSITIVE VIDEOS")
    print("=" * 70)
    
    total_positive = 0
    for keyword in positive_keywords:
        downloaded = search_and_download(
            keyword, 
            positive_dir, 
            max_results=videos_per_keyword,
            label="positive"
        )
        total_positive += downloaded
        
        # Kiểm tra nếu đã đủ số lượng
        if total_positive >= num_videos:
            break
        
        time.sleep(3)  # Nghỉ giữa các lần tìm kiếm
    
    # Tải negative videos
    print("\n" + "=" * 70)
    print("TẢI NEGATIVE VIDEOS")
    print("=" * 70)
    
    total_negative = 0
    for keyword in negative_keywords:
        downloaded = search_and_download(
            keyword,
            negative_dir,
            max_results=videos_per_keyword,
            label="negative"
        )
        total_negative += downloaded
        
        # Kiểm tra nếu đã đủ số lượng
        if total_negative >= num_videos:
            break
        
        time.sleep(3)  # Nghỉ giữa các lần tìm kiếm
    
    # Tóm tắt
    print("\n" + "=" * 70)
    print("KẾT QUẢ")
    print("=" * 70)
    print(f"\n✓ Đã tải thành công:")
    print(f"  - Positive videos: {total_positive}")
    print(f"  - Negative videos: {total_negative}")
    print(f"  - Tổng cộng: {total_positive + total_negative} videos")
    
    # Đếm file thực tế
    positive_files = len(list(positive_dir.glob("*.mp4")))
    negative_files = len(list(negative_dir.glob("*.mp4")))
    
    print(f"\n📁 Số file trong thư mục:")
    print(f"  - {positive_dir}: {positive_files} files")
    print(f"  - {negative_dir}: {negative_files} files")
    
    if positive_files > 0 and negative_files > 0:
        print("\n✅ Dataset đã sẵn sàng để fine-tune!")
        print("   Chạy lệnh: python videomae_finetune.py")
    else:
        print("\n⚠️  Chưa có đủ video. Vui lòng thử lại hoặc tải thủ công.")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

