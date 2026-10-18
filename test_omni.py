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
    response = client.models.generate_content(
        model="gemini-omni-1.1-flash-preview",
        contents="Hello from Vertex AI Omni Flash 1.1! Please describe your capabilities regarding video and image character replacement."
    )
    print("Omni Flash 1.1 response:")
    print(response.text)
except Exception as e:
    print(f"Error testing omni-flash-1.1: {e}")
