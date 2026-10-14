from pathlib import Path
from datetime import datetime, timezone
import logging
import uuid

import cv2
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from analyzers.video_analyzer import analyze_video


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trustra.video")

app = FastAPI(
    title="TRUSTRA 2.0 - AI Video Analyzer",
    description="Video upload and frame-based AI analysis API",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
MAX_FILE_SIZE = 100 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


@app.get("/")
def home():
    return {
        "project": "TRUSTRA 2.0",
        "module": "AI Video Analyzer",
        "message": "Backend is running successfully!",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "module": "video",
    }


def validate_video_file(video_path: Path) -> None:
    """
    Verify that OpenCV can open the uploaded file
    and read at least one frame.
    """
    capture = cv2.VideoCapture(str(video_path))

    try:
        if not capture.isOpened():
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a readable video.",
            )

        success, frame = capture.read()

        if not success or frame is None:
            raise HTTPException(
                status_code=400,
                detail="The video contains no readable frames.",
            )
    finally:
        capture.release()


@app.post("/api/analyzers/video")
async def upload_video(file: UploadFile = File(...)):
    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()

    if not original_name:
        raise HTTPException(
            status_code=400,
            detail="Please select a video file.",
        )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Use MP4, AVI, MOV, MKV, or WEBM.",
        )

    safe_filename = f"{uuid.uuid4().hex}{extension}"
    destination = UPLOAD_DIR / safe_filename
    total_size = 0

    try:
        # Stream upload to disk to avoid loading the entire file into memory.
        with destination.open("wb") as output:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Video exceeds the 100 MB upload limit.",
                    )

                output.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        # Check whether this is a readable video.
        validate_video_file(destination)

        # Run the project's existing AI video analyzer.
        result = analyze_video(destination)

        if not isinstance(result, dict) or "analysis" not in result:
            raise RuntimeError("The analyzer returned an invalid response.")

        analysis = result["analysis"]

        if not isinstance(analysis, dict):
            raise RuntimeError("The analysis result is invalid.")

        frames_analysed = analysis.get("frames_analysed", 0)

        if not isinstance(frames_analysed, int) or frames_analysed <= 0:
            raise HTTPException(
                status_code=422,
                detail="No video frames could be analysed. Try another video.",
            )

        fake_count = analysis.get("fake_label_count", 0)

        report = {
            "analysisId": uuid.uuid4().hex,
            "module": "video",
            "status": "completed",
            "analysis_status": result.get("analysis_status", "completed"),
            "analysis_type": result.get(
                "analysis_type",
                "sampled_frame_classification",
            ),
            "filename": original_name,
            "checkedAt": datetime.now(timezone.utc).isoformat(),
            "summary": (
                f"Analysed {frames_analysed} sampled frames. "
                f"{fake_count} were labelled Fake by the model."
            ),
            "analysis": analysis,
            "findings": analysis.get("findings", []),
            "recommendations": analysis.get("recommendations", []),
            "limitations": analysis.get("limitations", []),
        }

        return report

    except HTTPException:
        raise

    except (ValueError, FileNotFoundError) as exc:
        logger.warning("Video could not be analysed: %s", exc)

        raise HTTPException(
            status_code=400,
            detail="The video could not be processed. Try another supported video.",
        ) from exc

    except Exception:
        logger.exception("Video analysis failed.")

        raise HTTPException(
            status_code=500,
            detail=(
                "Video analysis failed. Please try again. "
                "Check the backend terminal for diagnostic details."
            ),
        )

    finally:
        await file.close()

        # Remove temporary uploaded video after success or failure.
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            logger.exception("Could not remove a temporary uploaded video.")