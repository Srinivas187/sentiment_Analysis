import React, { useState, useEffect } from 'react';
import './index.css';
import AuthPage from './components/AuthPage';
import PredictPage from './components/PredictPage';
import ChatPage from './components/ChatPage';
import StatusPage from './components/StatusPage';

const TABS = [
  { id: 'predict', label: '🔍 Predict',  icon: '🔍' },
  { id: 'chat',    label: '💬 Chat',     icon: '💬' },
  { id: 'status',  label: '📊 Status',   icon: '📊' },
];

export default function App() {
  const [user, setUser]     = useState(null);
  const [tab, setTab]       = useState('predict');
  const [authNotice, setAuthNotice] = useState('');

  useEffect(() => {
    const handleAuthExpired = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setAuthNotice('Your session expired or is no longer valid. Please sign in again.');
      setUser(null);
    };

    window.addEventListener('auth:expired', handleAuthExpired);
    const stored = localStorage.getItem('user');
    const token  = localStorage.getItem('token');
    if (stored && token) {
      try { setUser(JSON.parse(stored)); } catch { /* ignore */ }
    }

    return () => window.removeEventListener('auth:expired', handleAuthExpired);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setAuthNotice('');
    setUser(null);
  };

  if (!user) return <AuthPage onLogin={(u) => { setAuthNotice(''); setUser(u); }} notice={authNotice} />;

  return (
    <>
      {/* ── Navbar ── */}
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="icon">🧠</span>
          <span>SentimentAI &mdash; Batch-8</span>
        </div>
        <div className="navbar-actions">
          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            👤 {user.name || user.email}
          </span>
          <button id="logout-btn" className="btn btn-ghost" onClick={handleLogout}>
            🚪 Logout
          </button>
        </div>
      </nav>

      {/* ── Main ── */}
      <div className="main-content">
        {/* Tabs */}
        <div className="tabs">
          {TABS.map((t) => (
            <button
              key={t.id}
              id={`tab-${t.id}`}
              className={`tab-btn ${tab === t.id ? 'active' : ''}`}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {tab === 'predict' && <PredictPage />}
        {tab === 'chat'    && <ChatPage />}
        {tab === 'status'  && <StatusPage />}
      </div>
    </>
  );
}
