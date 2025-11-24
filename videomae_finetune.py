"""
Script fine-tune VideoMAE để phân loại video tích cực/tiêu cực
"""
import os
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoProcessor,
    AutoModelForVideoClassification,
    TrainingArguments,
    Trainer
)
from extract_frames import load_video
import numpy as np
from pathlib import Path

# Cấu hình
primary_model_name = "MCG-NJU/videomae-base-finetuned-kinetics-400"  # model fine-tuned trên Kinetics-400 (khó truy cập)
fallback_model_name = "MCG-NJU/videomae-base"  # model base công khai
model_name = primary_model_name
num_frames = 16
batch_size = 2
learning_rate = 5e-5
num_epochs = 3

# Đường dẫn dataset
dataset_path = "dataset"  # Thay đổi theo đường dẫn dataset của bạn
positive_folder = os.path.join(dataset_path, "positive")
negative_folder = os.path.join(dataset_path, "negative")


class VideoDataset(Dataset):
    """Dataset cho video classification"""
    
    def __init__(self, video_paths, labels, processor, num_frames=16):
        self.video_paths = video_paths
        self.labels = labels
        self.processor = processor
        self.num_frames = num_frames
    
    def __len__(self):
        return len(self.video_paths)
    
    def __getitem__(self, idx):
        video_path = self.video_paths[idx]
        label = self.labels[idx]
        
        try:
            # Trích xuất frames
            frames = load_video(video_path, self.num_frames)
            
            # Xử lý frames
            try:
                inputs = self.processor(
                    videos=list(frames),
                    return_tensors="pt"
                )
            except TypeError:
                inputs = self.processor(
                    images=list(frames),
                    return_tensors="pt"
                )
            
            # Loại bỏ batch dimension từ processor
            inputs = {k: v.squeeze(0) for k, v in inputs.items()}
            inputs['labels'] = torch.tensor(label, dtype=torch.long)
            
            return inputs
        except Exception as e:
            print(f"Lỗi khi xử lý video {video_path}: {e}")
            # Trả về dummy data nếu có lỗi
            dummy_frames = np.zeros((self.num_frames, 224, 224, 3), dtype=np.uint8)
            try:
                inputs = self.processor(videos=list(dummy_frames), return_tensors="pt")
            except TypeError:
                inputs = self.processor(images=list(dummy_frames), return_tensors="pt")
            inputs = {k: v.squeeze(0) for k, v in inputs.items()}
            inputs['labels'] = torch.tensor(label, dtype=torch.long)
            return inputs


def prepare_dataset():
    """Chuẩn bị dataset từ thư mục"""
    video_paths = []
    labels = []
    
    # Load videos tích cực (label = 0)
    if os.path.exists(positive_folder):
        for video_file in Path(positive_folder).glob("*.mp4"):
            video_paths.append(str(video_file))
            labels.append(0)  # 0 = positive
    
    # Load videos tiêu cực (label = 1)
    if os.path.exists(negative_folder):
        for video_file in Path(negative_folder).glob("*.mp4"):
            video_paths.append(str(video_file))
            labels.append(1)  # 1 = negative
    
    if len(video_paths) == 0:
        raise ValueError(
            f"Không tìm thấy video nào trong {positive_folder} hoặc {negative_folder}\n"
            "Vui lòng tạo dataset với cấu trúc:\n"
            "dataset/\n"
            "  ├── positive/\n"
            "  │   ├── video1.mp4\n"
            "  │   └── ...\n"
            "  └── negative/\n"
            "      ├── video1.mp4\n"
            "      └── ..."
        )
    
    print(f"Tìm thấy {len(video_paths)} videos:")
    print(f"  - Positive: {labels.count(0)} videos")
    print(f"  - Negative: {labels.count(1)} videos")
    
    # Chia train/val (80/20)
    split_idx = int(len(video_paths) * 0.8)
    train_paths = video_paths[:split_idx]
    train_labels = labels[:split_idx]
    val_paths = video_paths[split_idx:]
    val_labels = labels[split_idx:]
    
    return train_paths, train_labels, val_paths, val_labels


def collate_fn(batch):
    """Custom collate function để xử lý batch"""
    # Lấy keys từ batch đầu tiên
    keys = batch[0].keys()
    
    # Tạo batch dictionary
    batch_dict = {}
    for key in keys:
        if key == 'labels':
            batch_dict[key] = torch.stack([item[key] for item in batch])
        else:
            # Stack các tensors
            batch_dict[key] = torch.stack([item[key] for item in batch])
    
    return batch_dict


def main():
    print("=" * 50)
    print("VideoMAE Fine-tuning cho Positive/Negative Classification")
    print("=" * 50)
    
    # Load processor và model
    print("\n1. Đang tải processor và model...")
    global model_name
    try:
        print(f"   - Đang thử model: {model_name}")
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModelForVideoClassification.from_pretrained(model_name)
    except Exception as load_err:
        print(f"❌ Không thể tải model '{model_name}': {load_err}")
        print(f"   ➜ Thử fallback model '{fallback_model_name}'")
        model_name = fallback_model_name
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModelForVideoClassification.from_pretrained(model_name)
    
    print(f"✓ Đã tải model '{model_name}' thành công")

    # Thay đổi số lượng classes thành 2 (positive/negative)
    model.config.num_labels = 2
    model.classifier = torch.nn.Linear(model.config.hidden_size, 2)
    print("✓ Đã tải xong và cấu hình model cho 2 classes")
    
    # Chuẩn bị dataset
    print("\n2. Đang chuẩn bị dataset...")
    train_paths, train_labels, val_paths, val_labels = prepare_dataset()
    
    train_dataset = VideoDataset(train_paths, train_labels, processor, num_frames)
    val_dataset = VideoDataset(val_paths, val_labels, processor, num_frames)
    print("✓ Đã chuẩn bị xong dataset")
    
    # Tạo DataLoader
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./videomae_finetuned",
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        logging_dir="./logs",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
    )
    
    # Định nghĩa compute_metrics
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        accuracy = (predictions == labels).mean()
        return {"accuracy": accuracy}
    
    # Tạo Trainer
    print("\n3. Bắt đầu training...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )
    
    # Train
    trainer.train()
    
    # Lưu model
    print("\n4. Đang lưu model...")
    trainer.save_model("./videomae_finetuned_final")
    processor.save_pretrained("./videomae_finetuned_final")
    print("✓ Đã lưu model tại: ./videomae_finetuned_final")
    
    print("\n" + "=" * 50)
    print("Hoàn thành fine-tuning!")
    print("=" * 50)
    print("\nĐể sử dụng model đã fine-tune:")
    print("  model = AutoModelForVideoClassification.from_pretrained('./videomae_finetuned_final')")
    print("  processor = AutoProcessor.from_pretrained('./videomae_finetuned_final')")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTraining bị dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

