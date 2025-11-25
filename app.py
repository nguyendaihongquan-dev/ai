"""
FastAPI backend phục vụ inference cho VideoMAE.
Chạy server:

    uvicorn app:app --reload
"""
from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from inference_service import load_inference_components, predict_from_path

CHUNK_SIZE = 2 * 1024 * 1024  # 2MB
MAX_FILE_SIZE_MB = 300

app = FastAPI(
    title="Video Sentiment Service",
    version="0.1.0",
    description="API phân loại video Positive/Negative dựa trên VideoMAE fine-tune.",
)


def _cleanup_file(path: Optional[str]) -> None:
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


async def _download_video(video_url: str) -> str:
    """
    Tải video từ URL bất đồng bộ (chạy requests trong thread).
    """

    def _download_sync() -> str:
        response = requests.get(video_url, stream=True, timeout=120)
        response.raise_for_status()
        total_bytes = 0
        suffix = Path(video_url).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in response.iter_content(CHUNK_SIZE):
                if not chunk:
                    continue
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise ValueError("Kích thước video vượt quá giới hạn 300MB.")
                tmp.write(chunk)
        return tmp.name

    return await asyncio.to_thread(_download_sync)


async def _save_upload_file(upload: UploadFile) -> str:
    """
    Lưu file upload về đĩa để inference.
    """
    suffix = Path(upload.filename or "upload.mp4").suffix or ".mp4"
    total_bytes = 0
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        while True:
            chunk = await upload.read(CHUNK_SIZE)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValueError("Kích thước video vượt quá giới hạn 300MB.")
            tmp.write(chunk)
    finally:
        tmp.close()
        await upload.seek(0)
    return tmp.name


async def _ensure_components_loaded():
    """
    Đảm bảo processor + model đã được load (dùng cho startup và lazy-load).
    """
    processor = getattr(app.state, "processor", None)
    model = getattr(app.state, "model", None)
    if processor is None or model is None:
        processor, model = await asyncio.to_thread(load_inference_components)
        app.state.processor = processor
        app.state.model = model


@app.on_event("startup")
async def startup_event():
    await _ensure_components_loaded()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Giải phóng reference (Torch sẽ tự GC).
    """
    app.state.processor = None
    app.state.model = None


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/predict")
async def predict_endpoint(
    video_url: Optional[str] = Form(default=None),
    video_file: Optional[UploadFile] = File(default=None),
):
    """
    Nhận URL video hoặc upload file, trả về nhãn Positive/Negative.
    """
    if not video_url and not video_file:
        raise HTTPException(status_code=400, detail="Cần truyền video_url hoặc video_file.")
    if video_url and video_file:
        raise HTTPException(status_code=400, detail="Chỉ chọn một trong video_url hoặc video_file.")

    temp_path = None
    try:
        await _ensure_components_loaded()
        if video_url:
            temp_path = await _download_video(video_url)
        else:
            assert video_file is not None
            temp_path = await _save_upload_file(video_file)

        result = predict_from_path(temp_path, app.state.processor, app.state.model)
        return JSONResponse(
            {
                "label": result["label_name"],
                "label_index": result["label_index"],
                "confidence": result["confidence"],
                "probabilities": result["probabilities"],
                "source": "url" if video_url else "upload",
            }
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Lỗi tải video: {exc}") from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Lỗi nội bộ: {exc}") from exc
    finally:
        _cleanup_file(temp_path)


