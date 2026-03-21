import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

const ALERT_COLORS = {
  critical: { bg: '#fef2f2', border: '#fca5a5', text: '#dc2626', badge: '#fee2e2' },
  warning:  { bg: '#fffbeb', border: '#fcd34d', text: '#d97706', badge: '#fef3c7' },
  safe:     { bg: '#f0fdf4', border: '#86efac', text: '#16a34a', badge: '#dcfce7' }
}

const URGENCY_COLORS = {
  today: { bg: '#fef2f2', text: '#dc2626' },
  soon:  { bg: '#fffbeb', text: '#d97706' },
  later: { bg: '#f0fdf4', text: '#16a34a' }
}

export default function Dashboard({ user }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => { fetchDashboard() }, [])

  const fetchDashboard = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/dashboard/${user.user_id}`)
      setData(res.data)
    } catch (e) {
      setError('Could not load dashboard. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '4rem', color: '#64748b' }}>
      Loading your dashboard...
    </div>
  )

  if (error) return (
    <div style={{ background: '#fef2f2', color: '#dc2626',
      padding: '1rem', borderRadius: 8, marginTop: '1rem' }}>
      {error}
    </div>
  )

  const { summary, review_queue, backlog_alerts } = data

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: 22, fontWeight: 700 }}>
          Good morning, {summary?.user?.name?.split(' ')[0]} 👋
        </h1>
        <p style={{ color: '#64748b', fontSize: 14, marginTop: 4 }}>
          Here's your study plan for today
        </p>
      </div>

      {/* Stat cards */}
      <div style={{ display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
        {[
          { label: 'Reviews due',    value: summary?.review_count  || 0, color: '#6366f1' },
          { label: 'Critical alerts',value: summary?.critical_count|| 0, color: '#dc2626' },
          { label: 'Quizzes today',  value: summary?.quiz_today    || 0, color: '#16a34a' },
          { label: 'Avg score',      value: `${summary?.avg_score  || 0}%`, color: '#d97706' },
        ].map(s => (
          <div key={s.label} style={{
            background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 12, padding: '1rem 1.25rem'
          }}>
            <div style={{ fontSize: 24, fontWeight: 700,
              color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 13, color: '#64748b',
              marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid',
        gridTemplateColumns: '1fr 1fr', gap: 20 }}>

        {/* Review queue */}
        <div>
          <h2 style={{ fontSize: 15, fontWeight: 600,
            marginBottom: 12, color: '#1e293b' }}>
            Today's review queue
          </h2>
          {review_queue?.length === 0 && (
            <div style={{ background: '#f0fdf4', border: '1px solid #86efac',
              borderRadius: 10, padding: '1rem', fontSize: 14, color: '#16a34a' }}>
              All caught up! No reviews due today.
            </div>
          )}
          {review_queue?.map(item => {
            const uc = URGENCY_COLORS[item.urgency] || URGENCY_COLORS.later
            return (
              <div key={item.id} style={{
                background: '#fff', border: '1px solid #e2e8f0',
                borderRadius: 10, padding: '12px 14px', marginBottom: 8
              }}>
                <div style={{ display: 'flex',
                  justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 500, fontSize: 14 }}>
                      {item.topic_name}
                    </div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                      {item.subject_name}
                    </div>
                  </div>
                  <span style={{
                    background: uc.bg, color: uc.text,
                    fontSize: 11, fontWeight: 600,
                    padding: '3px 8px', borderRadius: 99
                  }}>
                    {item.urgency === 'today' ? 'Today'
                      : item.urgency === 'soon' ? `${item.days_until}d`
                      : `${item.days_until}d`}
                  </span>
                </div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 6 }}>
                  {item.message}
                </div>
                <div style={{ marginTop: 8, height: 4,
                  background: '#f1f5f9', borderRadius: 99 }}>
                  <div style={{
                    height: '100%', borderRadius: 99,
                    width: `${Math.round(item.recall_prob * 100)}%`,
                    background: item.recall_prob > 0.6 ? '#16a34a'
                              : item.recall_prob > 0.4 ? '#d97706' : '#dc2626',
                    transition: 'width 0.6s ease'
                  }} />
                </div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 3 }}>
                  Recall: {Math.round(item.recall_prob * 100)}%
                </div>
              </div>
            )
          })}
        </div>

        {/* Backlog alerts */}
        <div>
          <h2 style={{ fontSize: 15, fontWeight: 600,
            marginBottom: 12, color: '#1e293b' }}>
            Backlog alerts
          </h2>
          {backlog_alerts?.length === 0 && (
            <div style={{ background: '#f0fdf4', border: '1px solid #86efac',
              borderRadius: 10, padding: '1rem', fontSize: 14, color: '#16a34a' }}>
              No backlog detected. Keep it up!
            </div>
          )}
          {backlog_alerts?.map(alert => {
            const ac = ALERT_COLORS[alert.alert_level] || ALERT_COLORS.safe
            return (
              <div key={alert.id} style={{
                background: ac.bg, border: `1px solid ${ac.border}`,
                borderRadius: 10, padding: '12px 14px', marginBottom: 8
              }}>
                <div style={{ display: 'flex',
                  justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14,
                      color: ac.text }}>
                      {alert.subject_name}
                    </div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                      {alert.exam_name} · {alert.exam_date}
                    </div>
                  </div>
                  <span style={{
                    background: ac.badge, color: ac.text,
                    fontSize: 11, fontWeight: 700,
                    padding: '3px 8px', borderRadius: 99
                  }}>
                    {alert.severity_label} {alert.severity_10}/10
                  </span>
                </div>
                <p style={{ fontSize: 12, color: '#475569',
                  marginTop: 8, lineHeight: 1.5 }}>
                  {alert.message}
                </p>
                {alert.catchup_plan && (
                  <div style={{ marginTop: 8, padding: '8px 10px',
                    background: 'rgba(255,255,255,0.6)',
                    borderRadius: 6, fontSize: 12, color: '#475569' }}>
                    {alert.catchup_plan.advice}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}