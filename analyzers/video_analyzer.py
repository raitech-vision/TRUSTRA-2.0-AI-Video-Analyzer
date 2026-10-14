import cv2
from pathlib import Path

from analyzers.ai_detector import analyze_frames

MAX_VIDEO_SIZE = 100 * 1024 * 1024
MAX_FRAMES = 120
TARGET_SAMPLED_FRAMES = 60


def extract_frames(video_path, output_dir):
    """Extract evenly distributed frames from a video."""

    video_path = Path(video_path)
    output_dir = Path(output_dir)

    if not video_path.is_file():
        raise FileNotFoundError("Video file was not found.")

    if video_path.stat().st_size > MAX_VIDEO_SIZE:
        raise ValueError("Video exceeds the 100 MB limit.")

    output_dir.mkdir(parents=True, exist_ok=True)

    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        video.release()
        raise ValueError("The uploaded file could not be opened as a video.")

    saved_frames = []

    try:
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames <= 0:
            raise ValueError("Could not determine the video's frame count.")

        sample_count = min(total_frames, MAX_FRAMES, TARGET_SAMPLED_FRAMES)

        frame_indices = sorted(set(
            round(i * (total_frames - 1) / max(sample_count - 1, 1))
            for i in range(sample_count)
        ))

        for frame_number in frame_indices:
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = video.read()

            if not success:
                continue

            frame_path = output_dir / f"frame_{frame_number}.jpg"

            if cv2.imwrite(str(frame_path), frame):
                saved_frames.append(frame_path)

    finally:
        video.release()

    if not saved_frames:
        raise ValueError("No readable frames could be extracted.")

    return saved_frames


def analyze_video(video_path):
    """Extract frames, analyze them, and return results."""

    video_path = Path(video_path)
    output_dir = video_path.parent / f"{video_path.stem}_frames"

    try:
        frames = extract_frames(video_path, output_dir)
        analysis = analyze_frames(frames)

        return {
            "video": video_path.name,
            "analysis_status": "completed",
            "analysis_type": "frame_based_image_classification",
            "analysis": analysis,
        }

    finally:
        if output_dir.exists():
            for frame in output_dir.iterdir():
                if frame.is_file():
                    try:
                        frame.unlink()
                    except OSError as exc:
                        print(f"Could not delete frame {frame}: {exc}")

            try:
                output_dir.rmdir()
                print(f"Temporary frame folder removed: {output_dir}")
            except OSError as exc:
                print(f"Could not remove frame folder {output_dir}: {exc}")