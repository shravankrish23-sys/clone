import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1"
)

# Use our swapped keyframe or original character image as starting reference!
image_path = r"d:\Clone\test_swap_result.png"
img = types.Image.from_file(location=image_path)

prompt = (
    "A funny caricature man with a long protruding nose and thick mustache wearing a gray-blue suit "
    "is squatting down outdoors on a concrete floor at night, tapping and opening a green coconut with a handheld tool, "
    "looking up toward the camera with a subtle smirk, natural fluid motion, cinematic lighting."
)

print("Starting video generation with Google Veo 3.1...")
operation = client.models.generate_videos(
    model="veo-3.1-generate-001",
    image=img,
    prompt=prompt,
    config=dict(
        duration_seconds=6,
        fps=24,
        aspect_ratio="9:16"
    )
)

print(f"Operation started: {operation.name}")
print("Polling operation until complete...")

while not operation.done:
    print("Video generation in progress... sleeping 10s")
    time.sleep(10)
    operation = client.operations.get(operation)

print("\n[SUCCESS] Operation completed!")
if operation.error:
    print(f"Operation error: {operation.error}")
else:
    result = operation.response
    if not result:
        result = operation.result
    print("Result:", result)
    if hasattr(result, "generated_videos") and result.generated_videos:
        for i, vid in enumerate(result.generated_videos):
            vid_path = os.path.join(r"d:\Clone", f"veo_output_{i+1}.mp4")
            if hasattr(vid, "video"):
                v = vid.video
                if hasattr(v, "video_bytes") and v.video_bytes:
                    with open(vid_path, "wb") as f:
                        f.write(v.video_bytes)
                    print(f"Saved video bytes to: {vid_path}")
                elif hasattr(v, "save"):
                    v.save(location=vid_path)
                    print(f"Saved video using .save() to: {vid_path}")
                elif hasattr(v, "uri") and v.uri:
                    print(f"Video URI: {v.uri}")
                    # Download uri if applicable
                    try:
                        client.files.download(file=v.uri, destination=vid_path)
                        print(f"Downloaded from uri to: {vid_path}")
                    except Exception as err:
                        print(f"Download err: {err}")
    else:
        print("No generated_videos found in result.")
