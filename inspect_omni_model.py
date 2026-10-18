import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

client = genai.Client(vertexai=True, project=project_id, location="us-central1")
m = client.models.get(model="gemini-omni-1.1-flash-preview")

print("--- Model Details for gemini-omni-1.1-flash-preview ---")
print("Name:", m.name)
print("Display Name:", getattr(m, "display_name", None))
print("Description:", getattr(m, "description", None))
print("Supported actions / modalities:", getattr(m, "supported_generation_methods", None))
for attr in dir(m):
    if not attr.startswith("_"):
        val = getattr(m, attr)
        if not callable(val):
            print(f"{attr}: {val}")
