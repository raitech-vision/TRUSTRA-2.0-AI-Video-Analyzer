from analyzers.ai_detector import classifier
from pathlib import Path
import sys

def test_image(image_path):
    path = Path(image_path)

    if not path.is_file():
        print(f"Image not found: {path}")
        return

    predictions = classifier(str(path))

    print(f"\nImage: {path.name}")
    for item in predictions:
        print(
            f"Label: {item['label']} | "
            f"Score: {item['score']:.4%}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m analyzers.evaluate_model "
            '"path-to-image"'
        )
    else:
        test_image(sys.argv[1])