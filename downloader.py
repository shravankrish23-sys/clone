import sys
import os
import yt_dlp

def download_instagram_video(url, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title).50s-%(id)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
    }

    print(f"Downloading from: {url}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # If merged to mp4:
        base, _ = os.path.splitext(filename)
        final_file = f"{base}.mp4" if os.path.exists(f"{base}.mp4") else filename
        print(f"\n[SUCCESS] Video downloaded successfully: {final_file}")
        return final_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python downloader.py <instagram_url>")
        sys.exit(1)
        
    url = sys.argv[1]
    download_instagram_video(url)
