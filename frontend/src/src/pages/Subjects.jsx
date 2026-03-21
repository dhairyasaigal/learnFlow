import { useState, useEffect } from 'react'
import axios from 'axios'

const API    = 'http://localhost:8000'
const STREAMS = ['PCM', 'PCB', 'Commerce', 'Arts', 'University']

export default function Subjects({ user }) {
  const [subjects, setSubjects] = useState([])
  const [form, setForm] = useState({
    name: '', stream: user.stream || 'PCM',
    exam_name: '', exam_date: '', chapters_total: 10
  })
  const [curriculum, setCurriculum] = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState('')
  const [success,    setSuccess]    = useState('')

  useEffect(() => { fetchSubjects() }, [])

  const fetchSubjects = async () => {
    const res = await axios.get(`${API}/subjects/${user.user_id}`)
    setSubjects(res.data.subjects)
  }

  const loadCurriculum = async (stream) => {
    setForm(f => ({ ...f, stream }))
    const res = await axios.get(`${API}/curriculum/${stream}`)
    setCurriculum(res.data.subjects)
  }

  const addSubject = async () => {
    if (!form.name || !form.exam_date) {
      setError('Subject name and exam date are required'); return
    }
    setLoading(true); setError(''); setSuccess('')
    try {
      await axios.post(`${API}/subjects/${user.user_id}`, form)
      setSuccess(`${form.name} added successfully!`)
      setForm({ name: '', stream: user.stream || 'PCM',
        exam_name: '', exam_date: '', chapters_total: 10 })
      fetchSubjects()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to add subject')
    } finally { setLoading(false) }
  }

  const daysToExam = (dateStr) => {
    if (!dateStr) return null
    const diff = Math.ceil(
      (new Date(dateStr) - new Date()) / (1000 * 60 * 60 * 24)
    )
    return diff
  }

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>
        Subjects
      </h1>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
        Manage your subjects and exam dates
      </p>

      <div style={{ display: 'grid',
        gridTemplateColumns: '1fr 1.4fr', gap: 24 }}>

        {/* Add subject form */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0',
          borderRadius: 12, padding: '1.5rem', height: 'fit-content' }}>
          <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>
            Add subject
          </h2>

          {error && (
            <div style={{ background: '#fef2f2', color: '#dc2626',
              padding: '10px 14px', borderRadius: 8,
              fontSize: 13, marginBottom: 14 }}>{error}</div>
          )}
          {success && (
            <div style={{ background: '#f0fdf4', color: '#16a34a',
              padding: '10px 14px', borderRadius: 8,
              fontSize: 13, marginBottom: 14 }}>{success}</div>
          )}

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>Stream</label>
            <select value={form.stream}
              onChange={e => loadCurriculum(e.target.value)}
              style={{ width: '100%', padding: '10px 12px',
                border: '1px solid #e2e8f0', borderRadius: 8,
                fontSize: 14, background: '#fff' }}>
              {STREAMS.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>Subject name</label>
            {curriculum ? (
              <select value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value,
                  chapters_total: curriculum[e.target.value]?.length || 10 })}
                style={{ width: '100%', padding: '10px 12px',
                  border: '1px solid #e2e8f0', borderRadius: 8,
                  fontSize: 14, background: '#fff' }}>
                <option value=''>Select from curriculum...</option>
                {Object.keys(curriculum).map(s => (
                  <option key={s} value={s}>
                    {s} ({curriculum[s].length} topics)
                  </option>
                ))}
              </select>
            ) : (
              <input value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                placeholder='e.g. Physics'
                style={{ width: '100%', padding: '10px 12px',
                  border: '1px solid #e2e8f0', borderRadius: 8,
                  fontSize: 14, outline: 'none' }}
              />
            )}
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>Exam name</label>
            <input value={form.exam_name}
              onChange={e => setForm({ ...form, exam_name: e.target.value })}
              placeholder='e.g. JEE Mains 2025'
              style={{ width: '100%', padding: '10px 12px',
                border: '1px solid #e2e8f0', borderRadius: 8,
                fontSize: 14, outline: 'none' }}
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>Exam date</label>
            <input type='date' value={form.exam_date}
              onChange={e => setForm({ ...form, exam_date: e.target.value })}
              style={{ width: '100%', padding: '10px 12px',
                border: '1px solid #e2e8f0', borderRadius: 8,
                fontSize: 14, outline: 'none' }}
            />
          </div>

          <div style={{ marginBottom: 18 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>
              Total chapters: {form.chapters_total}
            </label>
            <input type='range' min={5} max={50}
              value={form.chapters_total}
              onChange={e => setForm({
                ...form, chapters_total: parseInt(e.target.value) })}
              style={{ width: '100%' }}
            />
          </div>

          <button onClick={addSubject} disabled={loading} style={{
            width: '100%', padding: '11px',
            background: loading ? '#c7d2fe' : '#6366f1',
            color: '#fff', border: 'none', borderRadius: 8,
            fontSize: 14, fontWeight: 600, cursor: 'pointer'
          }}>
            {loading ? 'Adding...' : 'Add Subject'}
          </button>
        </div>

        {/* Subject list */}
        <div>
          <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>
            Your subjects ({subjects.length})
          </h2>
          {subjects.length === 0 && (
            <div style={{ background: '#f8fafc',
              border: '1px dashed #e2e8f0', borderRadius: 12,
              padding: '2rem', textAlign: 'center',
              color: '#94a3b8', fontSize: 14 }}>
              No subjects added yet. Add your first subject.
            </div>
          )}
          {subjects.map(s => {
            const days = daysToExam(s.exam_date)
            return (
              <div key={s.id} style={{
                background: '#fff', border: '1px solid #e2e8f0',
                borderRadius: 10, padding: '14px 16px', marginBottom: 10
              }}>
                <div style={{ display: 'flex',
                  justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 15 }}>
                      {s.name}
                    </div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 3 }}>
                      {s.stream} · {s.chapters_total} chapters
                    </div>
                    {s.exam_name && (
                      <div style={{ fontSize: 12, color: '#6366f1', marginTop: 3 }}>
                        {s.exam_name}
                      </div>
                    )}
                  </div>
                  {days !== null && (
                    <span style={{
                      background: days <= 14 ? '#fef2f2'
                                : days <= 30 ? '#fffbeb' : '#f0fdf4',
                      color: days <= 14 ? '#dc2626'
                           : days <= 30 ? '#d97706' : '#16a34a',
                      fontSize: 12, fontWeight: 600,
                      padding: '4px 10px', borderRadius: 99
                    }}>
                      {days > 0 ? `${days}d left` : 'Exam passed'}
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}