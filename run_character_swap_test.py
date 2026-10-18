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
    def __init__(self, task="edit", resolution="720p", aspect_ratio="16:9", **kwargs):
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
    """Initializes and returns the Google GenAI client using GEMINI_API_KEY or GOOGLE_API_KEY."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY or GOOGLE_API_KEY is not set in .env.\n"
            "Please obtain a standard API key from https://aistudio.google.com/app/apikey "
            "and add it to your .env file:\n"
            "GEMINI_API_KEY=your_actual_api_key"
        )
    client = genai.Client(api_key=api_key)
    
    # Wrap client.interactions.create to support contents=[...] and config=...
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


def run_character_swap(
    video_path=None,
    character_image_path=r"d:\Clone\main character\character.png",
    output_video_path="output_swapped_video.mp4"
):
    """
    Performs direct Video-to-Video character swapping using gemini-omni-1.1-flash
    via the Interactions API.
    """
    # 1. Locate source video clip from split/
    if not video_path:
        split_clips = glob.glob(r"d:\Clone\split\*.mp4")
        if not split_clips:
            raise FileNotFoundError("No split video clip found in 'd:\\Clone\\split\\'. Run split_video.py first.")
        video_path = split_clips[0]

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Source video not found: {video_path}")
    if not os.path.exists(character_image_path):
        raise FileNotFoundError(f"Character image not found: {character_image_path}")

    print(f"Source video clip: {video_path}")
    print(f"Reference character image: {character_image_path}")

    # 2. Authenticate client
    client = get_client()

    # 3. Upload video and character reference image
    print("\n[Step 1/3] Uploading video and character files via client.files.upload()...")
    uploaded_video = client.files.upload(file=video_path)
    uploaded_char = client.files.upload(file=character_image_path)
    print(f"Uploaded video reference: {uploaded_video.name}")
    print(f"Uploaded character reference: {uploaded_char.name}")

    # 4. Wait for both files to reach ACTIVE state
    print("\n[Step 2/3] Waiting for files to reach ACTIVE state...")
    wait_for_files_active(client, [uploaded_video, uploaded_char])

    # 5. Call Interactions API with gemini-omni-1.1-flash
    prompt = (
        "Swap the main person in the video with the character in the reference image. "
        "Preserve the original motion, actions, camera angles, lighting, and background "
        "while seamlessly replacing the subject with the character."
    )

    config = types.GenerateContentConfig(
        video_config=types.VideoConfig(
            task="edit",
            resolution="720p",
            aspect_ratio="16:9"
        )
    )

    print("\n[Step 3/3] Calling client.interactions.create with model='gemini-omni-1.1-flash'...")
    interaction = client.interactions.create(
        model="gemini-omni-1.1-flash",
        contents=[uploaded_video, uploaded_char, prompt],
        config=config
    )

    print("[SUCCESS] Interaction response received.")

    # 6. Parse interaction.outputs to extract and save the resulting video
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
                print(f"[SUCCESS] Video bytes saved to: {output_abs_path}")
                break
            elif hasattr(v, "uri") and v.uri:
                client.files.download(file=v.uri, destination=output_abs_path)
                saved = True
                print(f"[SUCCESS] Video downloaded from URI to: {output_abs_path}")
                break

        # Check direct uri on part
        if hasattr(part, "uri") and part.uri:
            client.files.download(file=part.uri, destination=output_abs_path)
            saved = True
            print(f"[SUCCESS] Video downloaded from URI to: {output_abs_path}")
            break

    if not saved:
        print("[INFO] Direct video bytes not found in outputs. Checking interaction object:")
        print(interaction)

    return output_abs_path


if __name__ == "__main__":
    try:
        run_character_swap()
    except Exception as e:
        print(f"\n[Execution Note]: {e}", file=sys.stderr)
