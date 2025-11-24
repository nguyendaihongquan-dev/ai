"""
Script để dự đoán video tích cực/tiêu cực bằng model đã fine-tune
"""
from transformers import AutoProcessor, AutoModelForVideoClassification
import torch
from extract_frames import load_video
import sys
import os

# Đường dẫn model đã fine-tune
MODEL_PATH = "./videomae_finetuned_final"

# Nhãn
LABELS = {0: "POSITIVE (Tích cực)", 1: "NEGATIVE (Tiêu cực)"}


def predict(video_path, model_path=MODEL_PATH):
    """
    Dự đoán video tích cực hay tiêu cực
    
    Args:
        video_path: Đường dẫn đến file video
        model_path: Đường dẫn đến model đã fine-tune
    
    Returns:
        label: Nhãn dự đoán (0=positive, 1=negative)
        score: Độ tin cậy
        label_name: Tên nhãn
    """
    # Kiểm tra model có tồn tại không
    if not os.path.exists(model_path):
        print(f"❌ Không tìm thấy model tại: {model_path}")
        print("Vui lòng fine-tune model trước bằng lệnh: python videomae_finetune.py")
        return None, None, None
    
    # Load model và processor
    print(f"Đang tải model từ: {model_path}")
    processor = AutoProcessor.from_pretrained(model_path)
    model = AutoModelForVideoClassification.from_pretrained(model_path)
    model.eval()
    print("✓ Đã tải model xong")
    
    # Trích xuất frames
    print(f"Đang xử lý video: {video_path}")
    frames = load_video(video_path)
    
    # Xử lý frames
    inputs = processor(videos=list(frames), return_tensors="pt")
    
    # Dự đoán
    with torch.no_grad():
        logits = model(**inputs).logits
    
    # Tính xác suất
    probs = torch.softmax(logits, dim=-1)
    pred_idx = probs.argmax(-1).item()
    score = probs[0][pred_idx].item()
    label_name = LABELS[pred_idx]
    
    return pred_idx, score, label_name


if __name__ == "__main__":
    # Lấy đường dẫn video từ tham số
    if len(sys.argv) < 2:
        print("Cách sử dụng: python videomae_predict.py <đường_dẫn_video> [đường_dẫn_model]")
        print("Ví dụ: python videomae_predict.py demo.mp4")
        print("      python videomae_predict.py demo.mp4 ./videomae_finetuned_final")
        sys.exit(1)
    
    video_path = sys.argv[1]
    model_path = sys.argv[2] if len(sys.argv) > 2 else MODEL_PATH
    
    try:
        label, score, label_name = predict(video_path, model_path)
        
        if label is not None:
            print("\n" + "=" * 50)
            print("KẾT QUẢ DỰ ĐOÁN")
            print("=" * 50)
            print(f"Video: {video_path}")
            print(f"Nhãn: {label_name}")
            print(f"Độ tin cậy: {score:.2%}")
            print("=" * 50)
            
            # Hiển thị xác suất cho cả 2 classes
            print("\nChi tiết:")
            print(f"  - POSITIVE: {score:.2%}" if label == 0 else f"  - POSITIVE: {1-score:.2%}")
            print(f"  - NEGATIVE: {1-score:.2%}" if label == 0 else f"  - NEGATIVE: {score:.2%}")
        
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file video: {video_path}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

