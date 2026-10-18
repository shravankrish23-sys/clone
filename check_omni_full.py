import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

# List of all standard Vertex AI locations
locations = [
    "us-central1", "us-east4", "us-west1", "us-west4", "us-east1",
    "europe-west1", "europe-west4", "europe-west9", "europe-west3",
    "asia-southeast1", "asia-northeast1", "asia-south1", "global"
]

models_to_check = [
    "gemini-omni-1.1-flash-preview",
    "gemini-omni-flash-preview",
]

print(f"Checking availability of Omni Flash models across Vertex AI regions for project '{project_id}'...\n")

for model_name in models_to_check:
    print(f"\n=== Probing model: {model_name} ===")
    found_regions = []
    for loc in locations:
        try:
            client = genai.Client(vertexai=True, project=project_id, location=loc)
            m = client.models.get(model=model_name)
            print(f"[FOUND] {model_name} exists in {loc}!")
            found_regions.append(loc)
        except Exception as e:
            msg = str(e)
            if "404" in msg:
                pass
            elif "403" in msg:
                print(f"[403 Access/Allowlist Required] {loc}: {msg[:120]}")
            else:
                print(f"[{loc}] {msg[:120]}")
    if not found_regions:
        print(f"Result for {model_name}: Not available in any checked region.")
    else:
        print(f"Result for {model_name}: Available in {found_regions}")
