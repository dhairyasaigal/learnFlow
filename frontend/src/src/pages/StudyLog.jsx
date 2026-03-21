import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function StudyLog({ user }) {
  const [subjects, setSubjects] = useState([])
  const [form, setForm] = useState({
    subject_id:     '',
    topics_covered: 0,
    study_time:     0,
    quiz_score:     0,
    days_skipped:   0,
    self_rating:    3,
    notes:          ''
  })
  const [loading,  setLoading]  = useState(false)
  const [result,   setResult]   = useState(null)
  const [error,    setError]    = useState('')

  useEffect(() => {
    axios.get(`${API}/subjects/${user.user_id}`)
      .then(r => setSubjects(r.data.subjects))
  }, [])

  const submit = async () => {
    if (!form.subject_id) {
      setError('Please select a subject'); return
    }
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await axios.post(
        `${API}/study-log/${user.user_id}`,
        { ...form, subject_id: parseInt(form.subject_id) }
      )
      setResult(res.data.backlog)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save log')
    } finally { setLoading(false) }
  }

  const field = (label, key, type = 'number', min = 0, max = 100) => (
    <div style={{ marginBottom: 14 }}>
      <label style={{ fontSize: 13, fontWeight: 500,
        display: 'block', marginBottom: 5, color: '#374151' }}>
        {label}
      </label>
      <input type={type} min={min} max={max}
        value={form[key]}
        onChange={e => setForm({ ...form,
          [key]: type === 'number' ? Number(e.target.value) : e.target.value })}
        style={{ width: '100%', padding: '10px 12px',
          border: '1px solid #e2e8f0', borderRadius: 8,
          fontSize: 14, outline: 'none' }}
      />
    </div>
  )

  const ALERT_COLORS = {
    critical: '#dc2626', warning: '#d97706', safe: '#16a34a'
  }

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>
        Log Study Session
      </h1>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
        Log offline study — AI updates your backlog prediction
      </p>

      <div style={{ display: 'grid',
        gridTemplateColumns: '1fr 1fr', gap: 24 }}>

        {/* Form */}
        <div style={{ background: '#fff', border: '1px solid #e2e8f0',
          borderRadius: 12, padding: '1.5rem' }}>

          {error && (
            <div style={{ background: '#fef2f2', color: '#dc2626',
              padding: '10px 14px', borderRadius: 8,
              fontSize: 13, marginBottom: 14 }}>{error}</div>
          )}

          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>Subject</label>
            <select value={form.subject_id}
              onChange={e => setForm({ ...form, subject_id: e.target.value })}
              style={{ width: '100%', padding: '10px 12px',
                border: '1px solid #e2e8f0', borderRadius: 8,
                fontSize: 14, background: '#fff' }}>
              <option value=''>Select subject...</option>
              {subjects.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          {field('Topics covered today', 'topics_covered', 'number', 0, 20)}
          {field('Study time (minutes)', 'study_time',     'number', 0, 480)}
          {field('Quiz / self-test score (0-100)', 'quiz_score', 'number', 0, 100)}
          {field('Days skipped recently', 'days_skipped',  'number', 0, 14)}

          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>
              Confidence rating (1-5)
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              {[1,2,3,4,5].map(n => (
                <button key={n}
                  onClick={() => setForm({ ...form, self_rating: n })}
                  style={{ flex: 1, padding: '8px',
                    border: `2px solid ${form.self_rating === n
                      ? '#6366f1' : '#e2e8f0'}`,
                    borderRadius: 8,
                    background: form.self_rating === n ? '#eef2ff' : '#fff',
                    color: form.self_rating === n ? '#6366f1' : '#64748b',
                    fontWeight: 600, cursor: 'pointer', fontSize: 14 }}>
                  {n}
                </button>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: 18 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>Notes (optional)</label>
            <textarea value={form.notes}
              onChange={e => setForm({ ...form, notes: e.target.value })}
              rows={3} placeholder='What did you study today?'
              style={{ width: '100%', padding: '10px 12px',
                border: '1px solid #e2e8f0', borderRadius: 8,
                fontSize: 14, outline: 'none', resize: 'vertical' }}
            />
          </div>

          <button onClick={submit} disabled={loading} style={{
            width: '100%', padding: '11px',
            background: loading ? '#c7d2fe' : '#6366f1',
            color: '#fff', border: 'none', borderRadius: 8,
            fontSize: 14, fontWeight: 600, cursor: 'pointer'
          }}>
            {loading ? 'Saving...' : 'Save Session'}
          </button>
        </div>

        {/* Backlog result */}
        <div>
          {!result && (
            <div style={{ background: '#f8fafc',
              border: '1px dashed #e2e8f0', borderRadius: 12,
              padding: '2rem', textAlign: 'center', color: '#94a3b8',
              fontSize: 14 }}>
              Backlog analysis will appear here after saving
            </div>
          )}
          {result && (
            <div style={{ background: '#fff',
              border: `2px solid ${ALERT_COLORS[result.alert_level]}22`,
              borderRadius: 12, padding: '1.5rem' }}>
              <div style={{ display: 'flex',
                justifyContent: 'space-between', alignItems: 'center',
                marginBottom: 16 }}>
                <h3 style={{ fontSize: 16, fontWeight: 600 }}>
                  {result.subject}
                </h3>
                <span style={{
                  background: `${ALERT_COLORS[result.alert_level]}18`,
                  color: ALERT_COLORS[result.alert_level],
                  fontWeight: 700, fontSize: 13,
                  padding: '4px 10px', borderRadius: 99
                }}>
                  {result.severity_label} · {result.severity_10}/10
                </span>
              </div>

              {/* Severity bar */}
              <div style={{ height: 8, background: '#f1f5f9',
                borderRadius: 99, marginBottom: 8 }}>
                <div style={{
                  height: '100%', borderRadius: 99,
                  width: `${result.severity_10 * 10}%`,
                  background: ALERT_COLORS[result.alert_level],
                  transition: 'width 0.6s ease'
                }} />
              </div>

              <p style={{ fontSize: 13, color: '#475569',
                lineHeight: 1.6, marginBottom: 14 }}>
                {result.message}
              </p>

              {result.catchup_plan && (
                <div style={{ background: '#f8fafc',
                  borderRadius: 8, padding: '12px 14px' }}>
                  <div style={{ fontSize: 12, fontWeight: 600,
                    color: '#374151', marginBottom: 6 }}>
                    Catch-up plan
                  </div>
                  <div style={{ fontSize: 13, color: '#475569',
                    lineHeight: 1.6 }}>
                    {result.catchup_plan.advice}
                  </div>
                  <div style={{ display: 'flex', gap: 16,
                    marginTop: 10, fontSize: 12, color: '#64748b' }}>
                    <span>
                      Chapters left: {result.catchup_plan.chapters_remaining}
                    </span>
                    <span>
                      Days to exam: {result.catchup_plan.days_to_exam}
                    </span>
                    <span>
                      Per day: {result.catchup_plan.chapters_per_day}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}