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

try:
    print("Testing gemini-2.5-flash-image...")
    res = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents="Generate an image of a funny caricature man with a giant nose in a suit squatting down."
    )
    print("Result:")
    print(res)
except Exception as e:
    print(f"Error: {e}")
