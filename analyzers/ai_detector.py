from pathlib import Path
from transformers import pipeline

MODEL_NAME = "dima806/deepfake_vs_real_image_detection"

print("Loading TRUSTRA AI model...")

classifier = pipeline(
    "image-classification",
    model=MODEL_NAME,
    device=-1,
)

print("TRUSTRA AI model loaded successfully!")


def analyze_frames(frame_paths):
    """Analyze sampled video frames and summarize model predictions."""

    if not frame_paths:
        raise ValueError("No frames were provided for analysis.")

    frame_results = []

    for frame_path in frame_paths:
        path = Path(frame_path)

        if not path.is_file():
            continue

        predictions = classifier(str(path))

        if not predictions:
            continue

        scores = {
            item["label"].strip().lower(): float(item["score"])
            for item in predictions
        }

        real_score = scores.get("real", 0.0)
        fake_score = scores.get("fake", 0.0)

        predicted_label = max(
            predictions,
            key=lambda item: item["score"]
        )["label"].strip().lower()

        if predicted_label not in {"real", "fake"}:
            predicted_label = "unknown"

        frame_results.append({
            "frame": path.name,
            "prediction": predicted_label.title(),
            "real_score": round(real_score, 4),
            "fake_score": round(fake_score, 4),
        })

    if not frame_results:
        raise ValueError("No frames could be analysed.")

    total_frames = len(frame_results)

    fake_count = sum(
        result["prediction"] == "Fake"
        for result in frame_results
    )

    real_count = sum(
        result["prediction"] == "Real"
        for result in frame_results
    )

    unknown_count = sum(
        result["prediction"] == "Unknown"
        for result in frame_results
    )

    average_fake_score = sum(
        result["fake_score"]
        for result in frame_results
    ) / total_frames

    highest_fake_score = max(
        result["fake_score"]
        for result in frame_results
    )

    # Preliminary screening only—not a verified deepfake detector.
    if fake_count > 0 or highest_fake_score >= 0.70:
        overall_result = "Suspicious"
    elif average_fake_score >= 0.40:
        overall_result = "Needs Further Review"
    else:
        overall_result = "No Strong Fake Signal Detected"

    findings = [{
        "code": "FRAME_BASED_CLASSIFICATION",
        "description": (
            "Sampled frames were analysed using an image-classification model."
        ),
        "evidence": (
            f"{total_frames} frames analysed; "
            f"{fake_count} labelled Fake and "
            f"{real_count} labelled Real."
        ),
    }]

    if overall_result == "Suspicious":
        findings.append({
            "code": "SUSPICIOUS_FRAME_SIGNAL",
            "description": (
                "At least one sampled frame received a Fake label "
                "or a high fake score."
            ),
            "evidence": (
                f"Highest fake score: {highest_fake_score:.2%}. "
                "Manual verification is required."
            ),
        })

    return {
        "frames_analysed": total_frames,
        "overall_result": overall_result,
        "real_label_count": real_count,
        "fake_label_count": fake_count,
        "unknown_label_count": unknown_count,
        "average_fake_score": round(average_fake_score, 4),
        "highest_fake_score": round(highest_fake_score, 4),
        "frame_results": frame_results,
        "findings": findings,
        "recommendations": [
            "Manually review suspicious frames.",
            "Verify the video using independent trusted sources.",
            "Do not treat model predictions as proof of manipulation.",
            "Use a labelled test dataset to evaluate precision, recall and accuracy.",
        ],
        "limitations": [
            "This model classifies images rather than complete videos.",
            "A frame labelled Real does not prove that the video is genuine.",
            "The thresholds are preliminary screening rules, not validated accuracy improvements.",
            "The average fake score is not a verified probability that the entire video is fake.",
            "Performance may vary across datasets, video quality and manipulation techniques.",
        ],
    }