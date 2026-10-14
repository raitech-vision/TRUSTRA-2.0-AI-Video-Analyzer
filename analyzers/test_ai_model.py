from pathlib import Path
from collections import Counter
from transformers import pipeline

MODEL_NAME = "dima806/deepfake_vs_real_image_detection"
FRAMES_DIR = Path("extracted_frames")

print("Loading pretrained AI model...")

classifier = pipeline(
    "image-classification",
    model=MODEL_NAME,
    device=-1
)

image_files = sorted(FRAMES_DIR.glob("*.jpg"))

if not image_files:
    print("No extracted frames found!")
    raise SystemExit(1)

print(f"\nFound {len(image_files)} frames.")

results_summary = []
fake_scores = []

for index, image_path in enumerate(image_files, start=1):
    predictions = classifier(str(image_path))

    scores = {
        item["label"].lower(): item["score"]
        for item in predictions
    }

    fake_score = scores.get("fake", 0.0)
    real_score = scores.get("real", 0.0)

    predicted_label = max(
        predictions,
        key=lambda item: item["score"]
    )["label"]

    results_summary.append(predicted_label)
    fake_scores.append(fake_score)

    print(
        f"Frame {index:02d}: "
        f"Prediction={predicted_label}, "
        f"Real={real_score:.4f}, "
        f"Fake={fake_score:.4f}"
    )

counts = Counter(label.lower() for label in results_summary)

print("\n========== VIDEO FRAME SUMMARY ==========")
print(f"Total frames analysed: {len(image_files)}")
print(f"Frames labelled Real: {counts.get('real', 0)}")
print(f"Frames labelled Fake: {counts.get('fake', 0)}")
print(
    f"Average fake-class score: "
    f"{sum(fake_scores) / len(fake_scores):.4f}"
)
print("\nNote: Frame predictions are not proof of video authenticity.")
print("This model is an image classifier, not a complete video detector.")