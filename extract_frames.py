import cv2
import numpy as np

def load_video(path, num_frames=16):
    """
    Trích xuất frames từ video
    
    Args:
        path: Đường dẫn đến file video
        num_frames: Số lượng frames cần trích xuất (mặc định 16)
    
    Returns:
        numpy array chứa các frames
    """
    # Mở video bằng OpenCV
    cap = cv2.VideoCapture(path)
    
    if not cap.isOpened():
        raise ValueError(f"Không thể mở video: {path}")
    
    # Lấy tổng số frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        cap.release()
        raise ValueError(f"Video không có frames: {path}")
    
    # Tính các vị trí frames cần lấy (rải đều)
    indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
    
    frames = []
    for idx in indices:
        # Đặt vị trí frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        
        if ret:
            # Chuyển từ BGR sang RGB (OpenCV dùng BGR, model cần RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
        else:
            # Nếu không đọc được frame, lấy frame gần nhất
            cap.set(cv2.CAP_PROP_POS_FRAMES, min(idx, total_frames - 1))
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
    
    cap.release()
    
    # Chuyển thành numpy array
    frames_array = np.array(frames)
    
    return frames_array

