import React, { useState } from 'react';
import { api } from '../utils/api';

export default function AuthPage({ onLogin, notice = '' }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(notice);
  const [success, setSuccess] = useState('');

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setSuccess('');
    setLoading(true);
    try {
      if (mode === 'login') {
        const res = await api.login({ email: form.email, password: form.password });
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('user', JSON.stringify(res.data.user));
        onLogin(res.data.user);
      } else {
        await api.register({ name: form.name, email: form.email, password: form.password });
        setSuccess('Registered! Please log in.');
        setMode('login');
        setForm({ name: '', email: form.email, password: '' });
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-logo">
          <span className="logo-icon">🧠</span>
          <h1>SentimentAI</h1>
          <p>Word Embedding Feature Design for Product Review Classification</p>
        </div>

        {error   && <div className="alert alert-danger">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="auth-name">Full Name</label>
              <input
                id="auth-name"
                type="text"
                name="name"
                placeholder="Your name"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>
          )}
          <div className="form-group">
            <label htmlFor="auth-email">Email</label>
            <input
              id="auth-email"
              type="email"
              name="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="auth-password">Password</label>
            <input
              id="auth-password"
              type="password"
              name="password"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
              required
            />
          </div>

          <button
            id="auth-submit"
            className="btn btn-primary"
            type="submit"
            disabled={loading}
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.8rem' }}
          >
            {loading ? <span className="spinner" /> : (mode === 'login' ? '🔓 Sign In' : '✨ Create Account')}
          </button>
        </form>

        <div className="auth-switch">
          {mode === 'login'
            ? <>Don't have an account? <button onClick={() => { setMode('register'); setError(''); }}>Register</button></>
            : <>Already have an account? <button onClick={() => { setMode('login'); setError(''); }}>Login</button></>}
        </div>
      </div>
    </div>
  );
}
