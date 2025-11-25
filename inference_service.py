"""
Tiện ích dùng chung để load model và chạy inference VideoMAE.
"""
from __future__ import annotations

import os
from typing import Dict, Tuple

import torch
from transformers import AutoProcessor, AutoModelForVideoClassification

from extract_frames import load_video

LABELS = {0: "POSITIVE (Tích cực)", 1: "NEGATIVE (Tiêu cực)"}
DEFAULT_MODEL_PATH = os.environ.get("VIDEOMAE_MODEL_PATH", "./videomae_finetuned_final")


def load_inference_components(model_path: str | None = None) -> Tuple[AutoProcessor, AutoModelForVideoClassification]:
    """
    Load processor + model một lần để tái sử dụng.
    """
    path = model_path or DEFAULT_MODEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Không tìm thấy model tại {path}. Hãy chạy videomae_finetune.py trước."
        )
    processor = AutoProcessor.from_pretrained(path)
    model = AutoModelForVideoClassification.from_pretrained(path)
    model.eval()
    return processor, model


def predict_from_path(
    video_path: str,
    processor: AutoProcessor,
    model: AutoModelForVideoClassification,
) -> Dict[str, float | str | int | Dict[str, float]]:
    """
    Chạy inference trên một video và trả về nhãn/kết quả xác suất.
    """
    frames = load_video(video_path)
    try:
        inputs = processor(videos=list(frames), return_tensors="pt")
    except TypeError:
        inputs = processor(images=list(frames), return_tensors="pt")

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=-1)[0]
    pred_idx = int(torch.argmax(probs).item())
    confidence = float(probs[pred_idx].item())

    return {
        "label_index": pred_idx,
        "label_name": LABELS.get(pred_idx, str(pred_idx)),
        "confidence": confidence,
        "probabilities": {
            LABELS.get(0, "0"): float(probs[0].item()),
            LABELS.get(1, "1"): float(probs[1].item()),
        },
    }


