import { useState } from "react";
import "./App.css";

function App() {
  const [video, setVideo] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleVideoChange = (event) => {
    const selectedVideo = event.target.files?.[0];

    setVideo(null);
    setResult(null);
    setMessage("");

    if (!selectedVideo) return;

    const allowedExtensions = /\.(mp4|avi|mov|mkv|webm)$/i;

    if (!allowedExtensions.test(selectedVideo.name)) {
      setMessage("Unsupported format. Select MP4, AVI, MOV, MKV, or WEBM.");
      event.target.value = "";
      return;
    }

    if (selectedVideo.size === 0) {
      setMessage("The selected file is empty.");
      event.target.value = "";
      return;
    }

    if (selectedVideo.size > 100 * 1024 * 1024) {
      setMessage("Video size must not exceed 100 MB.");
      event.target.value = "";
      return;
    }

    setVideo(selectedVideo);
  };

  const handleUpload = async () => {
    if (!video) {
      setMessage("Please select a video first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", video);

    setLoading(true);
    setMessage("Uploading video and running AI analysis...");
    setResult(null);

    try {
      const response = await fetch("/api/analyzers/video", {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : `Request failed with status ${response.status}.`
        );
      }

      setResult(data);
      setMessage("Video analysis completed successfully!");
    } catch (error) {
      console.error("Video upload error:", error);
      setMessage(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const analysis = result?.analysis;

  const formatPercent = (value) =>
    `${(Number(value || 0) * 100).toFixed(2)}%`;

  return (
    <main className="app">
      <header className="dashboard-header">
        <div className="brand-icon">T</div>

        <div>
          <h1>TRUSTRA <span>2.0</span></h1>
          <p className="brand-subtitle">AI-POWERED MEDIA ANALYSIS</p>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          Video Analyzer
        </div>
      </header>

      <section className="hero-section">
        <div className="hero-badge">AI VIDEO INTELLIGENCE</div>

        <h2>
          Analyze videos.
          <br />
          <span>Inspect the evidence.</span>
        </h2>

        <p>
          Upload a video to classify sampled frames and inspect
          possible manipulation indicators.
        </p>
      </section>

      <section className="upload-panel">
        <div className="section-heading">
          <div>
            <h3>Video Analysis</h3>
            <p>Choose a video file to get started.</p>
          </div>

          <span className="format-badge">MAX 100 MB</span>
        </div>

        <label className="upload-zone">
          <input
            type="file"
            accept=".mp4,.avi,.mov,.mkv,.webm"
            onChange={handleVideoChange}
            disabled={loading}
          />

          <span className="upload-icon">↑</span>

          <strong>
            {video ? "Video selected successfully" : "Choose a video"}
          </strong>

          <span className="upload-hint">
            {video
              ? video.name
              : "MP4, AVI, MOV, MKV or WEBM"}
          </span>

          <span className="browse-button">
            {video ? "Choose another file" : "Browse files"}
          </span>
        </label>

        {video && (
          <div className="selected-file">
            <div className="file-icon">▶</div>

            <div className="file-information">
              <strong>{video.name}</strong>
              <span>
                {(video.size / (1024 * 1024)).toFixed(2)} MB
              </span>
            </div>

            <span className="file-check">✓</span>
          </div>
        )}

        <button
          className="analyze-button"
          onClick={handleUpload}
          disabled={loading || !video}
        >
          {loading ? (
            <>
              <span className="spinner" />
              Analyzing video...
            </>
          ) : (
            <>Run AI Analysis <span>→</span></>
          )}
        </button>

        {message && (
          <div
            className={`message-box ${
              message.startsWith("Upload failed") ? "error-message" : ""
            }`}
            role="status"
            aria-live="polite"
          >
            {message}
          </div>
        )}

        {loading && (
          <p className="processing-note">
            Extracting frames and running the AI classifier.
            Please keep this page open.
          </p>
        )}
      </section>

      {analysis && (
        <section className="results" aria-live="polite">
          <div className="results-heading">
            <div>
              <span className="eyebrow">ANALYSIS REPORT</span>
              <h2>Video Analysis Results</h2>
            </div>

            <span className="completed-badge">
              <span className="status-dot" />
              Completed
            </span>
          </div>

          <div className="report-meta">
            <span>
              <strong>Analysis ID</strong>
              <code>{result.analysisId || "Not available"}</code>
            </span>

            <span>
              <strong>File</strong>
              <span>{video?.name || result.filename}</span>
            </span>
          </div>

          <div className="summary-banner">
            <span className="summary-icon">✦</span>

            <div>
              <strong>Analysis summary</strong>
              <p>{result.summary || "Frame analysis completed."}</p>
            </div>
          </div>

          <h3 className="section-title">Analysis Overview</h3>

          <div className="stats-grid">
            <article className="stat-card">
              <span className="stat-label">Frames Analyzed</span>
              <strong className="stat-number">
                {analysis.frames_analysed}
              </strong>
              <span className="stat-description">Sampled frames</span>
            </article>

            <article className="stat-card real-card">
              <span className="stat-label">Labeled Real</span>
              <strong className="stat-number">
                {analysis.real_label_count}
              </strong>
              <span className="stat-description">Model predictions</span>
            </article>

            <article className="stat-card fake-card">
              <span className="stat-label">Labeled Fake</span>
              <strong className="stat-number">
                {analysis.fake_label_count}
              </strong>
              <span className="stat-description">Model predictions</span>
            </article>

            <article className="stat-card">
              <span className="stat-label">Unknown</span>
              <strong className="stat-number">
                {analysis.unknown_label_count ?? 0}
              </strong>
              <span className="stat-description">Unclassified frames</span>
            </article>
          </div>

          <div className="score-panel">
            <div className="score-heading">
              <div>
                <h3>Average Fake-Classification Score</h3>
                <p>Average model score across sampled frames</p>
              </div>

              <strong className="score-value">
                {formatPercent(analysis.average_fake_score)}
              </strong>
            </div>

            <div
              className="score-track"
              role="progressbar"
              aria-label="Average fake-classification score"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.min(
                100,
                Math.max(
                  0,
                  Number(analysis.average_fake_score || 0) * 100
                )
              )}
            >
              <div
                className="score-fill"
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      Number(analysis.average_fake_score || 0) * 100
                    )
                  )}%`,
                }}
              />
            </div>

            <p className="score-disclaimer">
              This is a model classification score, not a verified
              probability that the complete video is fake.
            </p>
          </div>

          <div className="report-section">
            <h3 className="section-title">Findings</h3>

            {result.findings?.length ? (
              <div className="information-list">
                {result.findings.map((finding, index) => (
                  <article
                    className="information-card"
                    key={`${finding.code}-${index}`}
                  >
                    <span className="information-icon">i</span>

                    <div>
                      <strong>{finding.code}</strong>
                      <p>{finding.description}</p>

                      {finding.evidence && (
                        <p className="evidence-text">
                          Evidence: {finding.evidence}
                        </p>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <p>No findings were returned by the API.</p>
            )}
          </div>

          <div className="report-section">
            <h3 className="section-title">Frame Predictions</h3>

            <div className="frame-results">
              {analysis.frame_results?.map((frame) => {
                const prediction = frame.prediction?.toLowerCase();

                const predictionClass =
                  prediction === "fake"
                    ? "prediction-fake"
                    : prediction === "real"
                      ? "prediction-real"
                      : "prediction-unknown";

                return (
                  <article
                    key={frame.frame}
                    className="frame-result"
                  >
                    <div className="frame-card-heading">
                      <strong>{frame.frame}</strong>

                      <span className={`prediction-badge ${predictionClass}`}>
                        {frame.prediction}
                      </span>
                    </div>

                    <div className="frame-score">
                      <div>
                        <span>Real score</span>
                        <strong>{formatPercent(frame.real_score)}</strong>
                      </div>

                      <div className="mini-track">
                        <div
                          className="mini-fill real-fill"
                          style={{
                            width: `${Math.min(
                              100,
                              Math.max(0, Number(frame.real_score || 0) * 100)
                            )}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="frame-score">
                      <div>
                        <span>Fake score</span>
                        <strong>{formatPercent(frame.fake_score)}</strong>
                      </div>

                      <div className="mini-track">
                        <div
                          className="mini-fill fake-fill"
                          style={{
                            width: `${Math.min(
                              100,
                              Math.max(0, Number(frame.fake_score || 0) * 100)
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>

          <div className="report-section">
            <h3 className="section-title">Recommendations</h3>

            <ul className="report-list">
              {result.recommendations?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="limitations-panel">
            <h3>Important Limitations</h3>

            <ul>
              {result.limitations?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>

            <p>
              <strong>Important:</strong> These predictions are based
              on sampled frames. They do not establish whether the
              complete video is genuine or manipulated.
            </p>
          </div>
        </section>
      )}

      <footer className="dashboard-footer">
        <strong>TRUSTRA 2.0</strong>
        <span>AI Video Analyzer · Experimental analysis tool</span>
      </footer>
    </main>
  );
}

export default App;