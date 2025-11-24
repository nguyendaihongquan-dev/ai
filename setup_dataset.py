"""
Script helper để tạo cấu trúc dataset mẫu
"""
import os
from pathlib import Path

def create_dataset_structure():
    """Tạo cấu trúc thư mục dataset"""
    base_dir = "dataset"
    positive_dir = os.path.join(base_dir, "positive")
    negative_dir = os.path.join(base_dir, "negative")
    
    # Tạo thư mục
    os.makedirs(positive_dir, exist_ok=True)
    os.makedirs(negative_dir, exist_ok=True)
    
    # Tạo file README trong mỗi thư mục
    readme_content = """# Hướng dẫn

Đặt các file video vào thư mục này:
- Thư mục 'positive': Chứa các video tích cực
- Thư mục 'negative': Chứa các video tiêu cực

Định dạng video hỗ trợ: .mp4, .avi, .mov, .mkv
"""
    
    with open(os.path.join(base_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✓ Đã tạo cấu trúc dataset:")
    print(f"  {base_dir}/")
    print(f"    ├── positive/")
    print(f"    ├── negative/")
    print(f"    └── README.txt")
    print("\nVui lòng đặt các video vào thư mục tương ứng:")
    print(f"  - Video tích cực → {positive_dir}/")
    print(f"  - Video tiêu cực → {negative_dir}/")

if __name__ == "__main__":
    create_dataset_structure()

