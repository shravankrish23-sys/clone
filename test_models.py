import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

print("Listing accessible models or testing capability...")
# Let's test generating a keyframe scene with Imagen 3 or Gemini on Vertex AI
try:
    models = client.models.list()
    print("Found models list:")
    for m in models:
        if "imagen" in m.name.lower() or "veo" in m.name.lower() or "flash" in m.name.lower():
            print(f" - {m.name}")
except Exception as e:
    print(f"List models exception: {e}")
