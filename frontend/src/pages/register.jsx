import { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

const API     = 'http://localhost:8000'
const STREAMS = [
  { value: 'PCM',        label: 'PCM — Science (JEE)'         },
  { value: 'PCB',        label: 'PCB — Science (NEET)'        },
  { value: 'Commerce',   label: 'Commerce'                    },
  { value: 'Arts',       label: 'Arts / Humanities'           },
  { value: 'University', label: 'University (Placements/DSA)' },
]

export default function Register({ onLogin }) {
  const [form, setForm] = useState({
    name: '', email: '', password: '', stream: 'PCM'
  })
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    if (!form.name || !form.email || !form.password) {
      setError('All fields are required'); return
    }
    setLoading(true); setError('')
    try {
      await axios.post(`${API}/auth/register`, form)
      const login = await axios.post(`${API}/auth/login`, {
        email: form.email, password: form.password
      })
      onLogin(login.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Registration failed')
    } finally { setLoading(false) }
  }

  const inputStyle = {
    width: '100%', padding: '10px 12px',
    border: '1px solid #e2e8f0', borderRadius: 8,
    fontSize: 14, outline: 'none', boxSizing: 'border-box'
  }

  const labelStyle = {
    fontSize: 13, fontWeight: 500,
    color: '#374151', display: 'block', marginBottom: 5
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #f0f4ff, #faf5ff)'
    }}>
      <div style={{
        background: '#fff', borderRadius: 16,
        padding: '2.5rem', width: 420,
        border: '1px solid #e2e8f0',
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 28, fontWeight: 800,
            color: '#6366f1', marginBottom: 4 }}>
            Create account
          </div>
          <p style={{ color: '#64748b', fontSize: 13 }}>
            Join LearnFlow — built for Indian students
          </p>
        </div>

        {error && (
          <div style={{ background: '#fef2f2', color: '#dc2626',
            padding: '10px 14px', borderRadius: 8,
            fontSize: 13, marginBottom: 14 }}>
            {error}
          </div>
        )}

        <div style={{ marginBottom: 14 }}>
          <label style={labelStyle}>Full name</label>
          <input
            type='text' value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            placeholder='Rahul Sharma'
            style={inputStyle}
          />
        </div>

        <div style={{ marginBottom: 14 }}>
          <label style={labelStyle}>Email</label>
          <input
            type='email' value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            placeholder='you@example.com'
            style={inputStyle}
          />
        </div>

        <div style={{ marginBottom: 14 }}>
          <label style={labelStyle}>Password</label>
          <input
            type='password' value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
            placeholder='min 6 characters'
            style={inputStyle}
          />
        </div>

        <div style={{ marginBottom: 22 }}>
          <label style={labelStyle}>Your stream</label>
          <select
            value={form.stream}
            onChange={e => setForm({ ...form, stream: e.target.value })}
            style={{ ...inputStyle, background: '#fff' }}
          >
            {STREAMS.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
          <p style={{ fontSize: 11, color: '#94a3b8', marginTop: 5 }}>
            This sets your subjects and curriculum automatically
          </p>
        </div>

        <button onClick={submit} disabled={loading} style={{
          width: '100%', padding: '12px',
          background: loading ? '#c7d2fe' : '#6366f1',
          color: '#fff', border: 'none', borderRadius: 8,
          fontSize: 15, fontWeight: 600,
          cursor: loading ? 'not-allowed' : 'pointer'
        }}>
          {loading ? 'Creating account...' : 'Create account'}
        </button>

        <p style={{ textAlign: 'center', marginTop: 16,
          fontSize: 13, color: '#64748b' }}>
          Already have an account?{' '}
          <Link to='/login' style={{ color: '#6366f1',
            fontWeight: 500, textDecoration: 'none' }}>
            Login
          </Link>
        </p>

        <p style={{ textAlign: 'center', marginTop: 10,
          fontSize: 13 }}>
          <Link to='/' style={{ color: '#94a3b8',
            textDecoration: 'none' }}>
            Back to home
          </Link>
        </p>
      </div>
    </div>
  )
}