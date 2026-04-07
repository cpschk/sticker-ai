"""
Generate placeholder avatar images for all supported emotions and save them
to assets/poses/{emotion}.png for visual review.

Run from the backend/ directory:
    python test_avatars.py
"""
from pathlib import Path
from app.services.image_manipulation import generate_placeholder_avatar

EMOTIONS = ["risa", "sorpresa", "enojo", "tristeza", "confusión", "sarcasmo", "default"]

output_dir = Path(__file__).parent / "assets" / "poses"
output_dir.mkdir(parents=True, exist_ok=True)

for emotion in EMOTIONS:
    img = generate_placeholder_avatar(emotion)
    out = output_dir / f"{emotion}.png"
    img.save(out, format="PNG")
    print(f"  OK  {out}")

print(f"\n{len(EMOTIONS)} avatars saved to {output_dir.resolve()}")
