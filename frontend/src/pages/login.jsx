import { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function Login({ onLogin }) {
  const [form, setForm]       = useState({ email: '', password: '' })
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    setLoading(true); setError('')
    try {
      const res = await axios.post(`${API}/auth/login`, form)
      onLogin(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Login failed')
    } finally { setLoading(false) }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #f0f4ff, #faf5ff)'
    }}>
      <div style={{
        background: '#fff', borderRadius: 16,
        padding: '2.5rem', width: 400,
        border: '1px solid #e2e8f0',
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ fontSize: 32, fontWeight: 800,
            color: '#6366f1', marginBottom: 4 }}>
            LearnFlow
          </div>
          <p style={{ color: '#64748b', fontSize: 14 }}>
            AI study companion for Indian students
          </p>
        </div>

        {error && (
          <div style={{ background: '#fef2f2', color: '#dc2626',
            padding: '10px 14px', borderRadius: 8,
            fontSize: 13, marginBottom: 16 }}>
            {error}
          </div>
        )}

        <div style={{ marginBottom: 14 }}>
          <label style={{ fontSize: 13, fontWeight: 500,
            color: '#374151', display: 'block', marginBottom: 5 }}>
            Email
          </label>
          <input
            type='email' value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            placeholder='you@example.com'
            style={{ width: '100%', padding: '10px 12px',
              border: '1px solid #e2e8f0', borderRadius: 8,
              fontSize: 14, outline: 'none',
              boxSizing: 'border-box' }}
          />
        </div>

        <div style={{ marginBottom: 22 }}>
          <label style={{ fontSize: 13, fontWeight: 500,
            color: '#374151', display: 'block', marginBottom: 5 }}>
            Password
          </label>
          <input
            type='password' value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            onKeyDown={e => e.key === 'Enter' && submit()}
            placeholder='••••••••'
            style={{ width: '100%', padding: '10px 12px',
              border: '1px solid #e2e8f0', borderRadius: 8,
              fontSize: 14, outline: 'none',
              boxSizing: 'border-box' }}
          />
        </div>

        <button onClick={submit} disabled={loading} style={{
          width: '100%', padding: '12px',
          background: loading ? '#c7d2fe' : '#6366f1',
          color: '#fff', border: 'none', borderRadius: 8,
          fontSize: 15, fontWeight: 600,
          cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'background 0.2s'
        }}>
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <p style={{ textAlign: 'center', marginTop: 18,
          fontSize: 13, color: '#64748b' }}>
          No account?{' '}
          <Link to='/register' style={{ color: '#6366f1',
            fontWeight: 500, textDecoration: 'none' }}>
            Register here
          </Link>
        </p>

        <p style={{ textAlign: 'center', marginTop: 12,
          fontSize: 13, color: '#64748b' }}>
          <Link to='/' style={{ color: '#94a3b8',
            textDecoration: 'none' }}>
            Back to home
          </Link>
        </p>
      </div>
    </div>
  )
}