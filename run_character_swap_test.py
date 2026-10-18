import glob
import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Compatibility Shim for types.VideoConfig & GenerateContentConfig(video_config=...)
# ---------------------------------------------------------------------------
class VideoConfigCompat:
    def __init__(self, task="edit", resolution="720p", aspect_ratio="9:16", **kwargs):
        self.task = task
        self.resolution = resolution
        self.aspect_ratio = aspect_ratio
        for k, v in kwargs.items():
            setattr(self, k, v)
            
    def __repr__(self):
        return f"VideoConfig(task={self.task!r}, resolution={self.resolution!r}, aspect_ratio={self.aspect_ratio!r})"

types.VideoConfig = VideoConfigCompat

OrigGenerateContentConfig = types.GenerateContentConfig
class PatchedGenerateContentConfig(OrigGenerateContentConfig):
    model_config = {**OrigGenerateContentConfig.model_config, "extra": "allow"}

types.GenerateContentConfig = PatchedGenerateContentConfig


def get_client():
    """
    Initializes and returns the Google GenAI client using GEMINI_API_KEY / GOOGLE_API_KEY,
    with automatic fallback to Google Cloud service_account.json credentials if available.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key or api_key.strip() == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set in d:\\Clone\\.env.\n"
            "Please add your Gemini API key (from https://aistudio.google.com/app/apikey) to .env:\n"
            "GEMINI_API_KEY=AIzaSy..."
        )
    print("[AUTH] Authenticating with Gemini API Key...")
    client = genai.Client(api_key=api_key.strip())

    # Wrap client.interactions.create to handle contents=[...] and config=...
    orig_create = client.interactions.create
    def wrapped_create(*args, **kwargs):
        if "contents" in kwargs and "input" not in kwargs:
            kwargs["input"] = kwargs.pop("contents")
        if "config" in kwargs:
            cfg = kwargs.pop("config")
            extra = kwargs.setdefault("extra_body", {})
            if hasattr(cfg, "model_dump"):
                extra["config"] = cfg.model_dump()
            elif isinstance(cfg, dict):
                extra["config"] = cfg
            else:
                extra["config"] = getattr(cfg, "__dict__", str(cfg))
        return orig_create(*args, **kwargs)
        
    client.interactions.create = wrapped_create
    return client


def ensure_part1_clip(split_dir=r"d:\Clone\split"):
    """
    Ensures that Part 1 of the split video exists in 9:16 aspect ratio.
    If split/ is empty or missing Part 1, split_video.py is automatically executed.
    """
    os.makedirs(split_dir, exist_ok=True)
    candidates = [
        os.path.join(split_dir, "part 1.mp4"),
        os.path.join(split_dir, "part_1.mp4"),
        os.path.join(split_dir, "clip_1.mp4"),
        os.path.join(split_dir, "001.mp4"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    print("[INFO] Part 1 not found in 'split/'. Automatically running split_video.py...")
    from split_video import split_video
    created = split_video()
    if created and os.path.exists(created[0]):
        return created[0]
        
    all_clips = sorted(glob.glob(os.path.join(split_dir, "*.mp4")))
    if all_clips:
        return all_clips[0]
        
    raise FileNotFoundError("Could not find or generate Part 1 clip in 'split/'.")


def wait_for_files_active(client, files, timeout=180):
    """Polls client.files.get() until all uploaded files reach the 'ACTIVE' state."""
    for f in files:
        print(f"Checking status of uploaded file '{f.name}'...")
        start_time = time.time()
        file_obj = client.files.get(name=f.name)
        state_str = str(getattr(file_obj, "state", "")).upper()
        
        while "ACTIVE" not in state_str:
            if "FAILED" in state_str:
                raise RuntimeError(f"Processing failed for uploaded file '{f.name}'.")
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timed out waiting for '{f.name}' to reach ACTIVE state.")
            print(f"Waiting for '{f.name}' (current state: {state_str})... sleeping 5s")
            time.sleep(5)
            file_obj = client.files.get(name=f.name)
            state_str = str(getattr(file_obj, "state", "")).upper()
            
        print(f"[OK] File '{f.name}' is ACTIVE and ready.")


def run_character_swap_part1(
    character_image_path=r"d:\Clone\main character\character.png",
    output_video_path="output_reel_part1.mp4"
):
    """
    Executes the direct Video-to-Video character swap specifically on Part 1
    in vertical Reel 9:16 aspect ratio using gemini-omni-1.1-flash.
    """
    # 1. Target Part 1 video clip specifically
    part1_video = ensure_part1_clip()
    if not os.path.exists(character_image_path):
        raise FileNotFoundError(f"Character image not found at: {character_image_path}")

    print("=" * 60)
    print("VERTICAL REEL (9:16) CHARACTER SWAP - PART 1")
    print("=" * 60)
    print(f"Target Video (Part 1) : {part1_video}")
    print(f"Character Reference   : {character_image_path}")
    print(f"Output Target         : {output_video_path}")
    print(f"Aspect Ratio          : 9:16 (Vertical Reel)")
    print(f"Resolution            : 720p")
    print("=" * 60)

    # 2. Authenticate
    client = get_client()

    # 3. Upload Part 1 Video and Character Image
    print("\n[Step 1/3] Uploading Part 1 video and character image via client.files.upload()...")
    uploaded_video = client.files.upload(file=part1_video)
    uploaded_char = client.files.upload(file=character_image_path)
    print(f"Uploaded Part 1 Video Ref : {uploaded_video.name}")
    print(f"Uploaded Character Ref    : {uploaded_char.name}")

    # 4. Wait for both files to reach ACTIVE state
    print("\n[Step 2/3] Polling files until ACTIVE state is reached...")
    wait_for_files_active(client, [uploaded_video, uploaded_char])

    # 5. Call Interactions API with gemini-omni-1.1-flash & 9:16 Reel config
    prompt = (
        "Swap the main person in the video with the character in the reference image. "
        "Maintain the vertical 9:16 framing, original motion, deep squat actions, camera angles, "
        "night lighting, and background setting while replacing the subject with the caricature character."
    )

    config = types.GenerateContentConfig(
        video_config=types.VideoConfig(
            task="edit",
            resolution="720p",
            aspect_ratio="9:16"
        )
    )

    print("\n[Step 3/3] Calling client.interactions.create with model='gemini-omni-1.1-flash' (9:16 Reel)...")
    interaction = client.interactions.create(
        model="gemini-omni-1.1-flash",
        contents=[uploaded_video, uploaded_char, prompt],
        config=config
    )

    print("[SUCCESS] Interaction response received from gemini-omni-1.1-flash.")

    # 6. Parse interaction.outputs and save output_reel_part1.mp4
    saved = False
    output_abs_path = os.path.abspath(output_video_path)

    outputs = getattr(interaction, "outputs", None) or getattr(interaction, "output", None) or []
    if not isinstance(outputs, list):
        outputs = [outputs]

    for part in outputs:
        # Check part.video.data or video_bytes
        if hasattr(part, "video"):
            v = part.video
            data = getattr(v, "data", None) or getattr(v, "video_bytes", None)
            if data:
                with open(output_abs_path, "wb") as f:
                    f.write(data)
                saved = True
                print(f"[SUCCESS] Swapped 9:16 video saved to: {output_abs_path}")
                break
            elif hasattr(v, "uri") and v.uri:
                client.files.download(file=v.uri, destination=output_abs_path)
                saved = True
                print(f"[SUCCESS] Swapped 9:16 video downloaded from URI to: {output_abs_path}")
                break

        # Check direct uri on part
        if hasattr(part, "uri") and part.uri:
            client.files.download(file=part.uri, destination=output_abs_path)
            saved = True
            print(f"[SUCCESS] Swapped 9:16 video downloaded from URI to: {output_abs_path}")
            break

    if not saved:
        print("\n[INFO] Checking raw interaction object:")
        print(interaction)

    return output_abs_path


if __name__ == "__main__":
    try:
        run_character_swap_part1()
    except Exception as e:
        print(f"\n[Execution Note]: {e}", file=sys.stderr)
