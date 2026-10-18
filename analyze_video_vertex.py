import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load variables from .env
load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def get_vertex_client():
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT is missing. Please set it in your .env file.")
    
    # Initialize the GenAI Client with Vertex AI backend
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )
    return client

def test_connection():
    print(f"Connecting to Google Cloud Vertex AI (Project: {project_id}, Location: {location})...")
    client = get_vertex_client()
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello! Confirm connection to Vertex AI."
    )
    print("\n[SUCCESS] Response from Gemini Flash:")
    print(response.text)

def analyze_video_clip(video_path, prompt="Describe what happens in this video clip in detail."):
    client = get_vertex_client()
    print(f"Analyzing {video_path} using Gemini Flash...")
    
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=video_bytes,
                mime_type="video/mp4",
            ),
            prompt
        ]
    )
    print("\n--- Analysis Result ---")
    print(response.text)
    return response.text

if __name__ == "__main__":
    test_connection()
