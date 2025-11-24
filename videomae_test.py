from transformers import AutoProcessor, AutoModelForVideoClassification
import torch
from extract_frames import load_video

# Model VideoMAE được pre-trained trên Kinetics-400
# Thử model chính thức từ HuggingFace
model_name = "MCG-NJU/videomae-base-finetuned-kinetics-400"

# Load processor và model
print("Đang tải processor và model...")
print("Lưu ý: Lần đầu tiên sẽ tải model từ HuggingFace (có thể mất vài phút)...")
try:
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModelForVideoClassification.from_pretrained(model_name)
    print("✓ Đã tải xong!")
except Exception as e:
    print(f"❌ Lỗi khi tải model: {e}")
    print("\nThử model thay thế...")
    # Thử model base nếu model fine-tuned không tải được
    try:
        model_name = "MCG-NJU/videomae-base"
        print(f"Đang thử model: {model_name}")
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModelForVideoClassification.from_pretrained(model_name)
        print("✓ Đã tải model base thành công!")
    except Exception as e2:
        print(f"❌ Lỗi: {e2}")
        raise

def predict(video_path):
    """
    Dự đoán hành động trong video
    
    Args:
        video_path: Đường dẫn đến file video
    
    Returns:
        pred_idx: Chỉ số của class dự đoán
        score: Độ tin cậy của dự đoán
        probs: Tất cả các xác suất
    """
    print(f"  - Đang trích xuất frames từ video...")
    frames = load_video(video_path)
    print(f"  - Đã trích xuất {len(frames)} frames")
    
    # Xử lý frames - VideoMAE processor có thể cần format khác
    # Thử với images thay vì videos
    print(f"  - Đang xử lý frames...")
    try:
        inputs = processor(videos=list(frames), return_tensors="pt")
    except TypeError:
        # Nếu không được, thử với images
        inputs = processor(images=list(frames), return_tensors="pt")
    
    # Dự đoán
    print(f"  - Đang chạy model để dự đoán...")
    with torch.no_grad():
        logits = model(**inputs).logits
    
    # Tính xác suất
    probs = logits.softmax(dim=-1)
    pred_idx = probs.argmax(-1).item()
    score = probs[0][pred_idx].item()
    probs_array = probs[0].cpu().numpy()
    
    return pred_idx, score, probs_array

if __name__ == "__main__":
    import sys
    import numpy as np
    
    # Lấy đường dẫn video từ tham số hoặc dùng mặc định
    video_path = sys.argv[1] if len(sys.argv) > 1 else "demo.mp4"
    
    try:
        print("\n" + "=" * 60)
        print("VIDEOMAE VIDEO CLASSIFICATION TEST")
        print("=" * 60)
        print(f"\n📹 Video: {video_path}")
        print(f"🤖 Model: {model_name}")
        print("\n" + "-" * 60)
        
        label, score, probs = predict(video_path)
        
        # Lấy top 5 predictions
        top5_indices = np.argsort(probs)[::-1][:5]
        top5_probs = probs[top5_indices]
        
        print("\n" + "=" * 60)
        print("KẾT QUẢ DỰ ĐOÁN")
        print("=" * 60)
        print(f"\n🏆 Top Prediction:")
        print(f"   Class: {label}")
        print(f"   Confidence: {score:.2%}")
        
        print(f"\n📊 Top 5 Predictions:")
        for i, (idx, prob) in enumerate(zip(top5_indices, top5_probs), 1):
            marker = "👉" if i == 1 else "  "
            print(f"   {marker} {i}. Class {idx}: {prob:.2%}")
        
        print("\n" + "=" * 60)
        print("✅ Test hoàn thành!")
        print("=" * 60 + "\n")
        
    except FileNotFoundError:
        print(f"\n❌ Không tìm thấy file video: {video_path}")
        print("Vui lòng đặt file video trong cùng thư mục hoặc cung cấp đường dẫn đầy đủ\n")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}\n")
        import traceback
        traceback.print_exc()

