import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

regions = ["us-central1", "us-east4", "europe-west4", "us-west1"]
veo_models = ["veo-2.0-generate-001", "veo-3.0-generate-001", "veo-3.1-generate-001", "veo-3.1-fast-generate-001"]

img = types.Image.from_file(location=r"d:\Clone\main charater\character.png")

for reg in regions:
    client = genai.Client(vertexai=True, project=project_id, location=reg)
    print(f"\n--- Checking region: {reg} ---")
    for vm in veo_models:
        try:
            op = client.models.generate_videos(
                model=vm,
                image=img,
                prompt="test",
                config=dict(duration_seconds=5)
            )
            print(f"[SUCCESS] {vm} is ACTIVE in {reg}!")
            break
        except Exception as e:
            msg = str(e)
            if "404" in msg:
                pass
            elif "403" in msg:
                print(f"[403 Permission/Allowlist] {vm} in {reg}: {msg[:100]}")
            else:
                print(f"[{vm} in {reg}]: {msg[:100]}")
