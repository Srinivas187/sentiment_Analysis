import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';

export default function StatusPage() {
  const [status, setStatus]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [trainMsg, setTrainMsg] = useState('');
  const [trainError, setTrainError] = useState('');
  const [uploadMsg, setUploadMsg] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileRef = React.useRef();

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await api.status();
      setStatus(res.data);
    } catch {
      setStatus(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchStatus(); }, []);

  const handleTrain = async () => {
    setTrainMsg(''); setTrainError('');
    setTraining(true);
    try {
      const res = await api.train();
      setTrainMsg(res.data.message);
    } catch (err) {
      setTrainError(err.response?.data?.error || 'Training request failed');
    } finally {
      setTraining(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploadMsg(''); setUploadError('');
    setUploading(true);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await api.uploadCSV(fd);
      setUploadMsg(res.data.message);
      fetchStatus();
    } catch (err) {
      setUploadError(err.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  return (
    <div>
      <div className="section-title">System Status & Management</div>
      <p className="section-subtitle">Monitor model health, trigger retraining, and manage training data.</p>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <span className="spinner" style={{ width: 36, height: 36, borderWidth: 3, borderTopColor: 'var(--primary-light)', borderColor: 'var(--border)' }} />
          <p style={{ marginTop: '1rem' }}>Fetching system status…</p>
        </div>
      ) : status ? (
        <>
          {/* Stats */}
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-value" style={{ color: status.model_loaded ? 'var(--positive)' : 'var(--negative)' }}>
                {status.model_loaded ? '✅' : '❌'}
              </div>
              <div className="stat-label">Model Loaded</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{status.model_version || 'N/A'}</div>
              <div className="stat-label">Model Version</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {status.model_accuracy ? `${(status.model_accuracy * 100).toFixed(1)}%` : 'N/A'}
              </div>
              <div className="stat-label">Accuracy</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: status.threshold_reached ? 'var(--neutral)' : 'var(--text)' }}>
                {status.new_reviews_count ?? 0}
              </div>
              <div className="stat-label">New Reviews</div>
            </div>
          </div>

          {/* Training threshold */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <div className="card-header"><span className="icon">📈</span> Training Threshold</div>
            <div className="progress-wrap">
              <div className="progress-label">
                <span>Reviews since last training</span>
                <span>{status.new_reviews_count ?? 0} / {status.training_threshold}</span>
              </div>
              <div className="progress-bar" style={{ height: 10 }}>
                <div
                  className="progress-fill"
                  style={{
                    width: `${Math.min(100, ((status.new_reviews_count ?? 0) / status.training_threshold) * 100)}%`,
                    background: status.threshold_reached
                      ? 'linear-gradient(90deg,var(--positive),#55efc4)'
                      : 'linear-gradient(90deg,var(--primary),var(--accent))'
                  }}
                />
              </div>
            </div>
            {status.threshold_reached && (
              <div className="alert alert-warning" style={{ marginTop: '0.75rem' }}>
                ⚠️ Retraining threshold reached! Consider triggering a training run below.
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="grid-2">
            {/* Train */}
            <div className="card">
              <div className="card-header"><span className="icon">🔄</span> Trigger Training</div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '1rem' }}>
                Sync the database to CSV and retrain the sentiment model. Training runs in the background.
              </p>
              {trainMsg   && <div className="alert alert-success">{trainMsg}</div>}
              {trainError && <div className="alert alert-danger">{trainError}</div>}
              <button
                id="train-btn"
                className="btn btn-accent"
                onClick={handleTrain}
                disabled={training}
                style={{ width: '100%', padding: '0.75rem' }}
              >
                {training ? <><span className="spinner" /> Starting...</> : '⚡ Start Training'}
              </button>
            </div>

            {/* Upload CSV */}
            <div className="card">
              <div className="card-header"><span className="icon">📂</span> Upload Training CSV</div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '1rem' }}>
                Upload a CSV with columns <code style={{ color: 'var(--accent)' }}>review_text</code>, <code style={{ color: 'var(--accent)' }}>sentiment</code>, and optionally <code style={{ color: 'var(--accent)' }}>rating</code>.
              </p>
              {uploadMsg   && <div className="alert alert-success">{uploadMsg}</div>}
              {uploadError && <div className="alert alert-danger">{uploadError}</div>}
              <input
                id="csv-upload"
                ref={fileRef}
                type="file"
                accept=".csv"
                onChange={handleUpload}
                disabled={uploading}
                style={{ width: '100%' }}
              />
              {uploading && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.75rem', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                  <span className="spinner" style={{ borderTopColor: 'var(--accent)', borderColor: 'var(--border)' }} />
                  Uploading…
                </div>
              )}
            </div>
          </div>

          {/* Latest model info */}
          {status.latest_training && (
            <div className="card" style={{ marginTop: '1.5rem' }}>
              <div className="card-header"><span className="icon">🏷️</span> Latest Training Log</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
                {[
                  ['Version', status.latest_training.model_version],
                  ['Accuracy', status.latest_training.accuracy != null ? `${(status.latest_training.accuracy * 100).toFixed(2)}%` : 'N/A'],
                  ['Trained On', status.latest_training.trained_on ? new Date(status.latest_training.trained_on).toLocaleString() : 'N/A'],
                ].map(([label, val]) => (
                  <div key={label}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.3rem' }}>{label}</div>
                    <div style={{ fontWeight: 600, color: 'var(--text)' }}>{val}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="alert alert-danger">
          ⚠️ Could not connect to backend. Make sure the Flask server is running at <strong>http://localhost:5000</strong>.
        </div>
      )}

      <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
        <button id="refresh-status" className="btn btn-ghost" onClick={fetchStatus} disabled={loading}>
          🔃 Refresh Status
        </button>
      </div>
    </div>
  );
}
