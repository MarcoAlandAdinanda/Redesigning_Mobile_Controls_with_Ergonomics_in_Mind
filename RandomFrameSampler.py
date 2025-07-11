import cv2
import os
import random

def get_n_random_frames(video_path, save_dir, n=1):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Cannot open video file: {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        print(f"No frames in video: {video_path}")
        return

    # Ensure we don't sample more frames than available
    n = min(n, total_frames)
    random_indices = sorted(random.sample(range(total_frames), n))

    base_name = os.path.splitext(os.path.basename(video_path))[0]

    for i, frame_idx in enumerate(random_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        success, frame = cap.read()
        if success:
            frame_filename = os.path.join(save_dir, f"{base_name}_random{i+1}.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"Saved: {frame_filename}")
        else:
            print(f"Failed to read frame {frame_idx} in {video_path}")

    cap.release()

def process_video_directory(input_dir, output_dir, video_extensions={'.mp4', '.avi', '.mov'}):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if any(filename.lower().endswith(ext) for ext in video_extensions):
            video_path = os.path.join(input_dir, filename)
            get_n_random_frames(video_path, output_dir, n=1)

if __name__ == "__main__":
    input_directory = "video"
    output_directory = "sample_frames"
    process_video_directory(input_directory, output_directory)