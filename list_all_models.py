import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

print("Listing all accessible models:")
for m in client.models.list():
    print(m.name)
