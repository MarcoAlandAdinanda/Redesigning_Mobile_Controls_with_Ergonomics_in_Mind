import cv2
import numpy as np
import csv
from tqdm import tqdm

def rgb_to_hsv(rgb_color):
    rgb_pixel = np.uint8([[rgb_color]])  # shape (1, 1, 3)
    hsv_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2HSV)
    return hsv_pixel[0][0]

def track_color_with_tolerance(video_path, target_rgb, tolerance=20, output_csv="tracked_touch.csv"):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    target_hsv = rgb_to_hsv(target_rgb)
    lower_bound = np.array([
        max(0, target_hsv[0] - tolerance),
        max(0, target_hsv[1] - tolerance),
        max(0, target_hsv[2] - tolerance)
    ])
    upper_bound = np.array([
        min(179, target_hsv[0] + tolerance),
        min(255, target_hsv[1] + tolerance),
        min(255, target_hsv[2] + tolerance)
    ])

    frame_count = 0
    seconds_passed = 0

    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp_frame", "x", "y"])

        with tqdm(total=total_frames, desc="Processing video") as pbar:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, lower_bound, upper_bound)

                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    largest = max(contours, key=cv2.contourArea)
                    M = cv2.moments(largest)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = -1, -1
                else:
                    cX, cY = -1, -1

                # save one data point per second
                if frame_count % fps == 0:
                    writer.writerow([seconds_passed, cX, cY])
                    seconds_passed += 1

                frame_count += 1
                pbar.update(1)

    cap.release()
    print(f"Tracking complete. Data saved to: {output_csv}")


if __name__ == "__main__":
    video_path = "video/gameplay_recording.mp4"
    target_rgb = (191, 193, 190) # touch icon color
    tolerance = 25

    track_color_with_tolerance(video_path, target_rgb, tolerance)