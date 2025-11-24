"""
Script để tải video từ YouTube và tổ chức thành dataset positive/negative
"""
import os
import sys
import subprocess
from pathlib import Path

def check_yt_dlp():
    """Kiểm tra xem yt-dlp đã được cài đặt chưa"""
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

def download_video(url, output_path):
    """Tải video từ YouTube URL"""
    try:
        cmd = [
            "python3", "-m", "yt_dlp",
            "-f", "best[ext=mp4]",
            "-o", str(output_path),
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"Lỗi khi tải video: {result.stderr}")
            return False
    except Exception as e:
        print(f"Lỗi: {e}")
        return False

def create_dataset_structure():
    """Tạo cấu trúc thư mục dataset"""
    base_dir = Path("dataset")
    positive_dir = base_dir / "positive"
    negative_dir = base_dir / "negative"
    
    positive_dir.mkdir(parents=True, exist_ok=True)
    negative_dir.mkdir(parents=True, exist_ok=True)
    
    return positive_dir, negative_dir

def main():
    print("=" * 60)
    print("YOUTUBE VIDEO DATASET DOWNLOADER")
    print("=" * 60)
    
    # Kiểm tra yt-dlp
    if not check_yt_dlp():
        print("yt-dlp chưa được cài đặt.")
        install_yt_dlp()
    
    # Tạo cấu trúc dataset
    positive_dir, negative_dir = create_dataset_structure()
    print(f"\n✓ Đã tạo cấu trúc dataset:")
    print(f"  - Positive: {positive_dir}")
    print(f"  - Negative: {negative_dir}")
    
    print("\n" + "=" * 60)
    print("HƯỚNG DẪN SỬ DỤNG")
    print("=" * 60)
    print("\nCách 1: Tải từng video một")
    print("  python download_youtube_dataset.py <url> <label>")
    print("  Ví dụ: python download_youtube_dataset.py https://youtube.com/watch?v=xxx positive")
    print("\nCách 2: Tải nhiều video từ file")
    print("  Tạo file urls.txt với format:")
    print("    https://youtube.com/watch?v=xxx1,positive")
    print("    https://youtube.com/watch?v=xxx2,negative")
    print("  Sau đó chạy: python download_youtube_dataset.py --file urls.txt")
    
    # Xử lý tham số dòng lệnh
    if len(sys.argv) < 2:
        print("\n" + "=" * 60)
        print("Chế độ tương tác")
        print("=" * 60)
        
        while True:
            print("\nNhập lệnh:")
            print("  1. Tải video (url, label)")
            print("  2. Tải từ file (--file <file_path>)")
            print("  3. Thoát (q)")
            
            choice = input("\nLựa chọn: ").strip()
            
            if choice == "q" or choice == "3":
                break
            elif choice == "1":
                url = input("Nhập YouTube URL: ").strip()
                label = input("Nhập label (positive/negative): ").strip().lower()
                
                if label not in ["positive", "negative"]:
                    print("❌ Label phải là 'positive' hoặc 'negative'")
                    continue
                
                output_dir = positive_dir if label == "positive" else negative_dir
                video_count = len(list(output_dir.glob("*.mp4")))
                output_path = output_dir / f"video_{video_count + 1:04d}.mp4"
                
                print(f"\nĐang tải video vào: {output_path}")
                if download_video(url, output_path):
                    print(f"✓ Đã tải thành công: {output_path}")
                else:
                    print(f"❌ Lỗi khi tải video")
            elif choice == "2":
                file_path = input("Nhập đường dẫn file: ").strip()
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            
                            parts = line.split(',')
                            if len(parts) != 2:
                                print(f"⚠️  Dòng {line_num} không đúng format, bỏ qua")
                                continue
                            
                            url, label = parts[0].strip(), parts[1].strip().lower()
                            if label not in ["positive", "negative"]:
                                print(f"⚠️  Dòng {line_num}: Label không hợp lệ, bỏ qua")
                                continue
                            
                            output_dir = positive_dir if label == "positive" else negative_dir
                            video_count = len(list(output_dir.glob("*.mp4")))
                            output_path = output_dir / f"video_{video_count + 1:04d}.mp4"
                            
                            print(f"\n[{line_num}] Đang tải: {url}")
                            if download_video(url, output_path):
                                print(f"✓ Đã tải: {output_path}")
                            else:
                                print(f"❌ Lỗi khi tải")
                else:
                    print(f"❌ Không tìm thấy file: {file_path}")
    
    elif sys.argv[1] == "--file":
        # Tải từ file
        if len(sys.argv) < 3:
            print("❌ Thiếu đường dẫn file")
            return
        
        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            print(f"❌ Không tìm thấy file: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(',')
                if len(parts) != 2:
                    print(f"⚠️  Dòng {line_num} không đúng format, bỏ qua")
                    continue
                
                url, label = parts[0].strip(), parts[1].strip().lower()
                if label not in ["positive", "negative"]:
                    print(f"⚠️  Dòng {line_num}: Label không hợp lệ, bỏ qua")
                    continue
                
                output_dir = positive_dir if label == "positive" else negative_dir
                video_count = len(list(output_dir.glob("*.mp4")))
                output_path = output_dir / f"video_{video_count + 1:04d}.mp4"
                
                print(f"\n[{line_num}] Đang tải: {url}")
                if download_video(url, output_path):
                    print(f"✓ Đã tải: {output_path}")
                else:
                    print(f"❌ Lỗi khi tải")
    
    else:
        # Tải một video
        if len(sys.argv) < 3:
            print("❌ Thiếu tham số. Sử dụng: python download_youtube_dataset.py <url> <label>")
            return
        
        url = sys.argv[1]
        label = sys.argv[2].lower()
        
        if label not in ["positive", "negative"]:
            print("❌ Label phải là 'positive' hoặc 'negative'")
            return
        
        output_dir = positive_dir if label == "positive" else negative_dir
        video_count = len(list(output_dir.glob("*.mp4")))
        output_path = output_dir / f"video_{video_count + 1:04d}.mp4"
        
        print(f"\nĐang tải video vào: {output_path}")
        if download_video(url, output_path):
            print(f"✓ Đã tải thành công: {output_path}")
        else:
            print(f"❌ Lỗi khi tải video")

if __name__ == "__main__":
    main()

