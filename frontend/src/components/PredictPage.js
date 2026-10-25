import React, { useState } from 'react';
import { api } from '../utils/api';

const SentimentResult = ({ result }) => {
  if (!result) return null;

  const { sentiment, confidence, probabilities, explanation } = result;
  const badgeClass = `badge badge-${sentiment}`;
  const fillClass  = `confidence-fill fill-${sentiment}`;

  const wordChips = explanation?.word_contributions || [];

  return (
    <div className="card" style={{ marginTop: '1.25rem', animation: 'fadeUp 0.3s ease' }}>
      <div className="card-header">
        <span className="icon">📊</span> Analysis Result
      </div>

      {/* Sentiment badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
        <span className={badgeClass} style={{ fontSize: '1rem', padding: '0.45rem 1.1rem' }}>
          {sentiment === 'positive' ? '😊' : sentiment === 'negative' ? '😞' : '😐'} {sentiment}
        </span>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
          {(confidence * 100).toFixed(1)}% confidence
        </span>
      </div>

      {/* Confidence bar */}
      <div className="confidence-bar-wrap">
        <div className="confidence-label">
          <span>Confidence</span><span>{(confidence * 100).toFixed(1)}%</span>
        </div>
        <div className="confidence-bar">
          <div className={fillClass} style={{ width: `${confidence * 100}%` }} />
        </div>
      </div>

      {/* Probability breakdown */}
      {probabilities && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Probability Breakdown
          </div>
          {['positive', 'neutral', 'negative'].map((s) => (
            <div key={s} className="progress-wrap">
              <div className="progress-label">
                <span style={{ textTransform: 'capitalize' }}>{s}</span>
                <span>{((probabilities[s] || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{
                  width: `${(probabilities[s] || 0) * 100}%`,
                  background: s === 'positive' ? 'linear-gradient(90deg,#00b894,#55efc4)'
                            : s === 'negative' ? 'linear-gradient(90deg,#d63031,#e17055)'
                            : 'linear-gradient(90deg,#fdcb6e,#fab1a0)'
                }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Key words */}
      {wordChips.length > 0 && (
        <div style={{ marginTop: '1.1rem' }}>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Influential Words
          </div>
          <div className="word-chips">
            {wordChips.map((w, i) => (
              <span
                key={i}
                className={`word-chip ${w.impact_score > 0.05 ? 'chip-positive' : w.impact_score < -0.05 ? 'chip-negative' : 'chip-neutral'}`}
                title={`Impact: ${w.impact_score.toFixed(4)}`}
              >
                {w.word}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};


export default function PredictPage() {
  const [text, setText] = useState('');
  const [rating, setRating] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await api.predict({ review_text: text, rating: rating ? parseInt(rating) : undefined });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed. Check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const sampleReviews = [
    "This product is absolutely amazing! Works perfectly and exceeded all my expectations.",
    "Terrible quality, broke within a week. Waste of money. Very disappointed.",
    "It's okay, nothing special. Does the job but nothing remarkable about it.",
  ];

  return (
    <div>
      <div className="section-title">Sentiment Prediction</div>
      <p className="section-subtitle">Enter a product review to classify its sentiment using our word embedding model.</p>

      <div className="grid-2">
        <div className="card">
          <div className="card-header"><span className="icon">✍️</span> Enter Review</div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="review-text">Review Text</label>
              <textarea
                id="review-text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="e.g. This product is fantastic! Highly recommend..."
                style={{ minHeight: '130px' }}
              />
            </div>

            <div className="form-group">
              <label htmlFor="review-rating">Rating (optional)</label>
              <select id="review-rating" value={rating} onChange={(e) => setRating(e.target.value)}>
                <option value="">Select rating...</option>
                {[1,2,3,4,5].map(r => <option key={r} value={r}>{'⭐'.repeat(r)} ({r}/5)</option>)}
              </select>
            </div>

            {error && <div className="alert alert-danger">{error}</div>}

            <button id="predict-btn" className="btn btn-primary" type="submit" disabled={loading || !text.trim()} style={{ width: '100%', padding: '0.8rem' }}>
              {loading ? <><span className="spinner" /> Analyzing...</> : '🔍 Analyze Sentiment'}
            </button>
          </form>

          <div className="divider" />
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.6rem', fontWeight: 600 }}>
            QUICK SAMPLES
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {sampleReviews.map((s, i) => (
              <button
                key={i}
                id={`sample-${i}`}
                className="btn btn-ghost"
                style={{ textAlign: 'left', fontSize: '0.8rem', padding: '0.5rem 0.8rem', justifyContent: 'flex-start' }}
                onClick={() => setText(s)}
              >
                {s.length > 70 ? s.slice(0, 70) + '…' : s}
              </button>
            ))}
          </div>
        </div>

        <div>
          {result ? <SentimentResult result={result} /> : (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '280px', opacity: 0.5 }}>
              <span style={{ fontSize: '3.5rem' }}>🤖</span>
              <p style={{ marginTop: '1rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                Results will appear here after analysis
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
