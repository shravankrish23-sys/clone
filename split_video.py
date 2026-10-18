import math
import os
import subprocess
import sys

def get_video_duration(video_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def split_video(video_path, segment_duration=10, output_dir=r"d:\Clone\split"):
    os.makedirs(output_dir, exist_ok=True)
    duration = get_video_duration(video_path)
    num_parts = math.ceil(duration / segment_duration)
    print(f"Total video duration: {duration:.2f}s | Splitting into {num_parts} parts in '{output_dir}'.")

    created_parts = []
    for i in range(num_parts):
        part_num = i + 1
        output_file = os.path.join(output_dir, f"part {part_num}.mp4")
        start_time = i * segment_duration
        
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(segment_duration),
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            output_file
        ]
        
        print(f"Generating Part {part_num} ({start_time}s to {min(start_time + segment_duration, duration):.2f}s) -> {output_file}")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        created_parts.append(output_file)
        
    print("\n[SUCCESS] All parts created successfully!")
    return created_parts

if __name__ == "__main__":
    target_video = r"d:\Clone\downloads\Video by lizhi678ss-DeJ8EX_TVFp.mp4"
    if len(sys.argv) > 1:
        target_video = sys.argv[1]
    
    split_video(target_video, segment_duration=10)
