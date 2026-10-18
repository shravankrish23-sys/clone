# Instagram Viral Reel Character Swap Pipeline (Higgsfield Gentusu Style)

An end-to-end automation pipeline to download Instagram videos at maximum quality without watermarks, split them into segments, and replace the main actor with a custom caricature character using **Google Cloud Vertex AI (Gemini Flash & Google Veo 3.1)**.

Inspired by **Higgsfield Gentusu**, this project transforms real viral video actions (e.g., deep squats opening a coconut) into hilarious caricature videos while keeping the original setting, realistic physics, and synced audio.

---

## 🌟 Features

1. **High-Quality Instagram Downloader (No Watermarks)**
   - Extracts direct CDN video & audio streams using `yt-dlp` and merges them via `ffmpeg`.
   - Bypasses Instagram's re-share watermarks to guarantee pure raw quality.

2. **Automated 10-Second Segmenter**
   - Automatically calculates total duration and performs frame-accurate splits into 10-second clips.
   - Saves all output segments inside the `split/` directory (`part 1.mp4`, `part 2.mp4`, etc.).

3. **Multimodal Scene & Motion Analysis (Gemini Flash)**
   - Extracts actor posture, head tilts, facial expressions, camera angles, lighting, and tool interactions.
   - Formulates dense conditioning prompts for video synthesis.

4. **Character Swapping & Keyframe Synthesis (Gemini 2.5 Flash Image)**
   - Takes reference portraits/full-body images of the custom character ([main character/character.png](main%20character/character.png)).
   - Inpaints/replaces the main actor with the character in the exact pose, attire (double-breasted suit), and lighting.

5. **Video-to-Video Animation (Google Veo 3.1)**
   - Animates the character in fluid motion directly on Google Cloud Vertex AI (`veo-3.1-generate-001`).
   - Automatically syncs and remuxes the original ambient audio, voice chatter, and tapping sound effects.

---

## 📁 Repository Structure

```text
├── downloads/                  # Directory for raw downloaded Instagram videos (.gitkeep)
├── split/                      # Directory for split 10-second video parts (.gitkeep)
├── main character/             # Reference asset directory
│   └── character.png           # Master reference character image (face & full body)
├── downloader.py               # Instagram video download script
├── split_video.py              # Video splitting automation
├── analyze_video_vertex.py     # Vertex AI connection test & video clip analyzer
├── run_character_swap_test.py  # Keyframe character replacement via gemini-2.5-flash-image
├── generate_veo_video.py       # Google Veo 3.1 video generation & audio sync script
├── VERTEX_AI_SETUP.md          # Complete Google Cloud Vertex AI setup documentation
├── .env.example                # Configuration template
├── .gitignore                  # Prevents committing secrets or video files
└── README.md                   # Project overview & documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (tested on 3.12)
- **FFmpeg** installed and accessible in your system `PATH`.
- A **Google Cloud Project** with Vertex AI enabled.

### 2. Installation
```powershell
pip install -r requirements.txt
# Or install core packages:
pip install yt-dlp google-genai python-dotenv
```

### 3. Configure Google Cloud Credentials
1. Follow [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md) to create a Google Cloud Service Account with the **Vertex AI User** role.
2. Download your JSON key and place it in the project root as `service_account.json`.
3. Create your `.env` file based on `.env.example`:
   ```env
   GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_APPLICATION_CREDENTIALS=d:\Clone\service_account.json
   ```

---

## 🛠️ Usage

### Step 1: Download an Instagram Video
```powershell
python downloader.py "https://www.instagram.com/reel/DeJ8EX_TVFp/"
```
Saves the video directly into the `downloads/` folder.

### Step 2: Split Video into 10-Second Parts
```powershell
python split_video.py "downloads/your_video.mp4"
```
Outputs `part 1.mp4`, `part 2.mp4`, etc., inside the `split/` directory.

### Step 3: Run Keyframe Character Swap
```powershell
python run_character_swap_test.py
```
Uses `gemini-2.5-flash-image` on Vertex AI to replace the person in the video with your character in `main character/character.png`.

### Step 4: Generate Full Motion Video with Google Veo 3.1
```powershell
python generate_veo_video.py
```
Synthesizes the full animated video using **Google Veo 3.1** on Vertex AI and merges the original audio track from the reel.

---

## 🧠 Notes on Vertex AI Models

- **Google Veo 3.1 (`veo-3.1-generate-001`)**: Google's official generative video model available in `us-central1`, generating fluid 9:16 vertical video from character keyframes and motion prompts.
- **Gemini 2.5 Flash Image (`gemini-2.5-flash-image`)**: Multimodal image generation model capable of inpainting and character replacement.
- **Gemini Omni Flash 1.1 (`gemini-omni-1.1-flash-preview`)**: Dedicated to real-time bidirectional streaming (speech-to-speech / live interactions) via Google's Interactions API.

---

## 🔒 Security
- Raw `.mp4` and `.m4a` video files are ignored by git to keep the repository lightweight.
- `.env` and `service_account.json` are strictly excluded in `.gitignore` to prevent leaking private credentials.
