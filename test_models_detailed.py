import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "imagen-3.0-generate-002",
    "veo-2.0-generate-001"
]

for m in models_to_test:
    try:
        if "veo" in m:
            print(f"Testing {m} availability...")
            model_info = client.models.get(model=m)
            print(f"[OK] {m} is available!")
        elif "imagen" in m:
            print(f"Testing {m}...")
            res = client.models.generate_images(
                model=m,
                prompt="A funny cartoon character with a long nose opening a coconut, 3d render",
                config=dict(number_of_images=1)
            )
            print(f"[OK] {m} generated an image successfully!")
        else:
            print(f"Testing {m}...")
            res = client.models.generate_content(model=m, contents="ping")
            print(f"[OK] {m} works! Response: {res.text.strip()[:30]}")
    except Exception as e:
        print(f"[FAILED] {m}: {e}\n")
