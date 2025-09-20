import cv2
from ultralytics import YOLO
import os

def summarize_video(input_path, output_path):
    print("🔍 Loading YOLOv8n model...")
    model = YOLO("yolov8n.pt")  # Lightweight model

    print(f"📂 Opening video: {input_path}")
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("❌ Failed to open input video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"🎞️ Video properties — FPS: {fps}, Width: {width}, Height: {height}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    written_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        results = model(frame)[0]
        classes = results.boxes.cls.cpu().numpy() if results.boxes.cls is not None else []

        # Class 0 is "person"
        person_detected = any(cls == 0 for cls in classes)

        if person_detected:
            out.write(frame)
            written_frames += 1

        if frame_count % 10 == 0:
            print(f"📸 Processed {frame_count} frames | Written: {written_frames}")

    cap.release()
    out.release()

    # If no frames were written, optionally delete empty output
    if written_frames == 0:
        print("⚠️ No person detected in any frame. Deleting empty output.")
        if os.path.exists(output_path):
            os.remove(output_path)

    print(f"✅ Summarization complete. Total frames: {frame_count}, Frames written: {written_frames}")
