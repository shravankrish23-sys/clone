import glob
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
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        # Fallback to moviepy if ffprobe is not available
        from moviepy import VideoFileClip
        with VideoFileClip(video_path) as clip:
            return float(clip.duration)

def split_video(video_path=None, max_duration=10.0, output_dir=r"d:\Clone\split"):
    """
    Splits video into chunks of maximum 8 to 10 seconds each,
    as required by gemini-omni-1.1-flash video processing limits (<= 10 seconds).
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Auto-detect source video from downloads/ if none provided
    if not video_path:
        downloads = glob.glob(r"d:\Clone\downloads\*.mp4")
        if not downloads:
            raise FileNotFoundError("No source .mp4 video found in 'downloads/' folder.")
        video_path = downloads[0]
        
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    duration = get_video_duration(video_path)
    # Strictly cap segment duration between 8 and 10 seconds
    segment_duration = min(max(max_duration, 8.0), 10.0)
    
    num_parts = math.ceil(duration / segment_duration)
    print(f"Source video: {video_path}")
    print(f"Total duration: {duration:.2f}s | Splitting into {num_parts} parts (max {segment_duration:.1f}s each) into '{output_dir}'.")

    created_parts = []
    for i in range(num_parts):
        part_num = i + 1
        output_file = os.path.join(output_dir, f"part {part_num}.mp4")
        start_time = i * segment_duration
        current_segment_duration = min(segment_duration, duration - start_time)
        
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(current_segment_duration),
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            output_file
        ]
        
        print(f"Generating Part {part_num}: {start_time:.2f}s to {(start_time + current_segment_duration):.2f}s ({current_segment_duration:.2f}s) -> {output_file}")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        created_parts.append(output_file)
        
    print("\n[SUCCESS] All parts created successfully under 10s limit!")
    return created_parts

if __name__ == "__main__":
    target_video = None
    if len(sys.argv) > 1:
        target_video = sys.argv[1]
    split_video(target_video)
