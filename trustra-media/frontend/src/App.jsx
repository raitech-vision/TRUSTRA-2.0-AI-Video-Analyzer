import { useState } from "react";
import "./App.css";

function App() {
  const [video, setVideo] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleVideoChange = (event) => {
    const selectedVideo = event.target.files[0];

    if (!selectedVideo) return;

    if (!selectedVideo.type.startsWith("video/")) {
      setMessage("Please select a valid video file.");
      setVideo(null);
      return;
    }

    setVideo(selectedVideo);
    setMessage("");
  };

  const handleUpload = async () => {
    if (!video) {
      setMessage("Please select a video first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", video);

    try {
      setLoading(true);
      setMessage("Uploading video and analysing frames...");

      const response = await fetch(
        "http://127.0.0.1:8000/api/analyzers/video",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Video upload failed.");
      }

      setMessage(JSON.stringify(data, null, 2));
    } catch (error) {
      setMessage(`Analysis failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app">
      <div className="card">
        <h1>
          TRUSTRA <span>2.0</span>
        </h1>

        <h2>AI Video Analyzer</h2>

        <p className="description">
          Upload a video to analyse sampled frames for potential deepfake
          indicators.
        </p>

        <label htmlFor="video-upload" className="upload-area">
          <span className="upload-icon">▶</span>
          <strong>Select your video</strong>
          <span>MP4, MOV, AVI, MKV or WEBM</span>
        </label>

        <input
          id="video-upload"
          type="file"
          accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm"
          onChange={handleVideoChange}
        />

        {video && (
          <p className="file-name">
            Selected: {video.name}
          </p>
        )}

        <button
          type="button"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "Analysing..." : "Analyse Video"}
        </button>

        {message && (
          <pre className="result">{message}</pre>
        )}

        <p className="notice">
          Important: The AI model classifies sampled video frames.
          Results are preliminary indicators, not proof that a complete
          video is real or manipulated.
        </p>
      </div>
    </main>
  );
}

export default App;