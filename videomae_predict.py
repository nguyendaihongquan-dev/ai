"""
Script để dự đoán video tích cực/tiêu cực bằng model đã fine-tune
"""
import os
import sys

from inference_service import (
    DEFAULT_MODEL_PATH,
    LABELS,
    load_inference_components,
    predict_from_path,
)


def predict(video_path, model_path=DEFAULT_MODEL_PATH):
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
    processor, model = load_inference_components(model_path)
    print("✓ Đã tải model xong")
    
    # Dự đoán
    print(f"Đang xử lý video: {video_path}")
    return predict_from_path(video_path, processor, model)


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
        result = predict(video_path, model_path)
        
        if result and result.get("label_name") is not None:
            label = result["label_index"]
            score = result["confidence"]
            label_name = result["label_name"]
            print("\n" + "=" * 50)
            print("KẾT QUẢ DỰ ĐOÁN")
            print("=" * 50)
            print(f"Video: {video_path}")
            print(f"Nhãn: {label_name}")
            print(f"Độ tin cậy: {score:.2%}")
            print("=" * 50)
            
            # Hiển thị xác suất cho cả 2 classes
            probs = result.get("probabilities", {})
            print("\nChi tiết:")
            print(f"  - POSITIVE: {probs.get(LABELS[0], 0):.2%}")
            print(f"  - NEGATIVE: {probs.get(LABELS[1], 0):.2%}")
        
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file video: {video_path}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

