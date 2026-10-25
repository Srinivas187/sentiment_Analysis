import React, { useState, useRef, useEffect } from 'react';
import { api } from '../utils/api';

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hi! I can help you analyze product reviews. Enter a review text below and ask me questions like "Analyze this review" or "Why is it negative?"' }
  ]);
  const [input, setInput]         = useState('');
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading]     = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages((m) => [...m, userMsg]);
    const msg = input;
    setInput('');
    setLoading(true);
    try {
      const res = await api.chat({ message: msg, review_text: reviewText });
      setMessages((m) => [...m, { role: 'bot', text: res.data.response }]);
    } catch (err) {
      setMessages((m) => [...m, {
        role: 'bot',
        text: '⚠️ ' + (err.response?.data?.error || 'Failed to get response. Is the backend running?')
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div>
      <div className="section-title">AI Chat Assistant</div>
      <p className="section-subtitle">Ask questions about review sentiment, word influence, and more.</p>

      <div className="grid-2">
        {/* Review context input */}
        <div className="card">
          <div className="card-header"><span className="icon">📝</span> Review Context</div>
          <div className="form-group">
            <label htmlFor="chat-review">Review Text (context for analysis)</label>
            <textarea
              id="chat-review"
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              placeholder="Paste a product review here to give context to the chatbot..."
              style={{ minHeight: '150px' }}
            />
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            💡 Try asking: "Analyze this review", "Why is it negative?", "What words are influential?"
          </div>
          <div className="divider" />
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '0.5rem' }}>SUGGESTED PROMPTS</div>
          {[
            'Analyze this review',
            'Why is it negative?',
            'What words influence the sentiment?',
          ].map((p, i) => (
            <button
              key={i}
              id={`chat-prompt-${i}`}
              className="btn btn-ghost"
              style={{ display: 'block', width: '100%', textAlign: 'left', marginBottom: '0.4rem', fontSize: '0.82rem' }}
              onClick={() => setInput(p)}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Chat window */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card-header"><span className="icon">💬</span> Conversation</div>

          <div className="chat-window">
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                {m.text}
              </div>
            ))}
            {loading && (
              <div className="chat-msg bot" style={{ opacity: 0.6 }}>
                <span className="spinner" style={{ borderTopColor: 'var(--primary-light)', borderColor: 'rgba(255,255,255,0.15)' }} />
                &nbsp; Thinking...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              id="chat-input"
              type="text"
              placeholder="Ask something about the review..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              disabled={loading}
            />
            <button
              id="chat-send"
              className="btn btn-primary"
              onClick={send}
              disabled={loading || !input.trim()}
              style={{ minWidth: '90px' }}
            >
              Send 🚀
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
