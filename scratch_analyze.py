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

video_path = r"d:\Clone\split\part 1.mp4"
with open(video_path, "rb") as f:
    video_bytes = f.read()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"),
        "Analyze this 10-second video clip in detail: Describe the main person, their posture, head movements, facial expressions, speech/mouth movements, gestures, camera motion, and background."
    ]
)
print("=== GEMINI FLASH ANALYSIS ===")
print(response.text)
