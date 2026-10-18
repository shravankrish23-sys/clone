import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

# Test with global location
for loc in ["global", "us-central1"]:
    print(f"\nTesting generate_content with location='{loc}'...")
    try:
        client = genai.Client(vertexai=True, project=project_id, location=loc)
        res = client.models.generate_content(
            model="gemini-omni-1.1-flash-preview",
            contents="Hello! Can you hear me?"
        )
        print(f"[SUCCESS] in {loc}: {res.text}")
    except Exception as e:
        print(f"[FAILED] in {loc}: {e}")
