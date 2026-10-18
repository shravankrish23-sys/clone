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

source_frame_path = r"d:\Clone\source_frame_1.png"
character_path = r"d:\Clone\main character\character.png"

with open(source_frame_path, "rb") as f:
    source_bytes = f.read()

with open(character_path, "rb") as f:
    char_bytes = f.read()

prompt = (
    "Image 1 shows a scene where a shirtless man is squatting down on a concrete floor outdoors at night, trying to open a green coconut with a tool. "
    "Image 2 shows a full-body and portrait reference of a distinctive caricature character (a tall man with a very long protruding nose, large mustache, frizzy balding hair on the sides, mismatched eyes, wearing a gray-blue double-breasted suit and yellow polo shirt). "
    "Task: Generate a new image replicating the exact scene, camera angle, night lighting, and concrete floor with beer bottles from Image 1, "
    "but REPLACE the squatting man with the funny character from Image 2. "
    "The character must maintain his exact facial features (huge nose, mustache, hair, eyes) and wear his tailored gray-blue suit and yellow polo while doing the deep squat and opening the green coconut. "
    "Maintain high photographic realism with the comedic character."
)

print("Calling gemini-2.5-flash-image to generate the swapped character frame...")
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[
        types.Part.from_bytes(data=source_bytes, mime_type="image/png"),
        types.Part.from_bytes(data=char_bytes, mime_type="image/png"),
        prompt
    ]
)

output_path = r"d:\Clone\test_swap_result.png"
found_image = False
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            found_image = True
            print(f"[SUCCESS] Swapped character image saved to: {output_path}")
        elif part.text:
            print("Model message:", part.text)

if not found_image:
    print("[INFO] No inline image returned directly in response. Output details:")
    print(response)
