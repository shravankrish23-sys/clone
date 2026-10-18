import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

img = types.Image.from_file(location=r"d:\Clone\main character\character.png")

print("Submitting test video generation to Veo 2.0...")
try:
    operation = client.models.generate_videos(
        model="veo-2.0-generate-001",
        image=img,
        prompt="The tall caricature man with long nose and suit squats down outdoors at night and taps on a green coconut with a tool, comedic facial expression.",
        config=dict(
            duration_seconds=5,
            fps=24,
            aspect_ratio="9:16"
        )
    )
    print("Operation started successfully!")
    print(f"Operation name: {operation.name}")
except Exception as e:
    print(f"Error starting Veo generation: {e}")
