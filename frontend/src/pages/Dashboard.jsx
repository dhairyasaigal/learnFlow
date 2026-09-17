import { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

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

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

function ScoreBar({ score, height = 6 }) {
  const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'
  return (
    <div style={{ height, background: '#f1f5f9', borderRadius: 99, overflow: 'hidden', marginTop: 6 }}>
      <div style={{
        width: `${score}%`, height: '100%', background: color,
        borderRadius: 99, transition: 'width 0.6s ease'
      }} />
    </div>
  )
}

export default function Dashboard({ user }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')
  const navigate = useNavigate()

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
      <div style={{ fontSize: 36, marginBottom: 12 }}>⚡</div>
      Loading your dashboard...
    </div>
  )

  if (error) return (
    <div style={{
      background: '#fef2f2', color: '#dc2626',
      padding: '1rem 1.25rem', borderRadius: 10,
      border: '1px solid #fca5a5', marginTop: '1rem', fontSize: 14
    }}>
      {error}
    </div>
  )

  const { summary, review_queue, backlog_alerts, weak_topics, recent_quizzes } = data
  const u = summary?.user || {}

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: '#1e293b', margin: 0 }}>
          {getGreeting()}, {u.name?.split(' ')[0] || 'Student'} 👋
        </h1>
        <p style={{ color: '#64748b', fontSize: 14, marginTop: 4, margin: 0 }}>
          Here's your study overview — streak: <strong style={{ color: '#6366f1' }}>
            🔥 {u.streak || 0} days
          </strong> &nbsp;·&nbsp; XP: <strong style={{ color: '#f59e0b' }}>
            ⭐ {u.xp || 0}
          </strong>
        </p>
      </div>

      {/* Stat cards */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 12, marginBottom: 24
      }}>
        {[
          { label: 'Reviews due',     value: summary?.review_count   || 0, color: '#6366f1', icon: '🔁' },
          { label: 'Critical alerts', value: summary?.critical_count || 0, color: '#dc2626', icon: '🚨' },
          { label: 'Quizzes today',   value: summary?.quiz_today     || 0, color: '#10b981', icon: '✏️' },
          { label: 'Avg score',       value: `${summary?.avg_score   || 0}%`, color: '#d97706', icon: '📊' },
        ].map(s => (
          <div key={s.label} style={{
            background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 14, padding: '16px 18px', cursor: 'default'
          }}>
            <div style={{ fontSize: 22 }}>{s.icon}</div>
            <div style={{ fontSize: 26, fontWeight: 800, color: s.color, marginTop: 4 }}>
              {s.value}
            </div>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>

        {/* Review queue */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: '#1e293b' }}>
              🔁 Today's Review Queue
            </h2>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>
              {review_queue?.length || 0} topics
            </span>
          </div>

          {review_queue?.length === 0 ? (
            <div style={{
              background: '#f0fdf4', border: '1px solid #86efac',
              borderRadius: 12, padding: '16px', fontSize: 14, color: '#16a34a', textAlign: 'center'
            }}>
              ✅ All caught up! No reviews due today.
            </div>
          ) : (
            review_queue.map(item => {
              const uc = URGENCY_COLORS[item.urgency] || URGENCY_COLORS.later
              return (
                <div key={item.id} style={{
                  background: '#fff', border: '1px solid #e2e8f0',
                  borderRadius: 12, padding: '12px 14px', marginBottom: 8
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14, color: '#1e293b' }}>
                        {item.topic_name}
                      </div>
                      <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                        {item.subject_name}
                      </div>
                    </div>
                    <span style={{
                      background: uc.bg, color: uc.text, fontSize: 11,
                      fontWeight: 700, padding: '3px 10px', borderRadius: 99
                    }}>
                      {item.urgency === 'today' ? 'TODAY' : `${item.days_until}d`}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 6 }}>{item.message}</div>
                  <ScoreBar score={Math.round((item.recall_prob || 0) * 100)} />
                  <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 3 }}>
                    Recall probability: {Math.round((item.recall_prob || 0) * 100)}%
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Backlog alerts */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: '#1e293b' }}>
              🚨 Backlog Alerts
            </h2>
            <span style={{ fontSize: 12, color: '#94a3b8' }}>
              {backlog_alerts?.filter(a => a.alert_level !== 'safe').length || 0} active
            </span>
          </div>

          {backlog_alerts?.length === 0 ? (
            <div style={{
              background: '#f0fdf4', border: '1px solid #86efac',
              borderRadius: 12, padding: '16px', fontSize: 14, color: '#16a34a', textAlign: 'center'
            }}>
              🎉 No backlog detected — keep up the pace!
            </div>
          ) : (
            backlog_alerts.map(alert => {
              const ac = ALERT_COLORS[alert.alert_level] || ALERT_COLORS.safe
              return (
                <div key={alert.id} style={{
                  background: ac.bg, border: `1px solid ${ac.border}`,
                  borderRadius: 12, padding: '12px 14px', marginBottom: 8
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 14, color: ac.text }}>
                        {alert.subject_name}
                      </div>
                      <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                        {alert.exam_name} · {alert.exam_date}
                      </div>
                    </div>
                    <span style={{
                      background: ac.badge, color: ac.text,
                      fontSize: 11, fontWeight: 700,
                      padding: '3px 10px', borderRadius: 99
                    }}>
                      {alert.severity_label} {alert.severity_10}/10
                    </span>
                  </div>
                  <p style={{ fontSize: 12, color: '#475569', marginTop: 8, lineHeight: 1.5, margin: '8px 0 0' }}>
                    {alert.message}
                  </p>
                  {alert.catchup_plan?.advice && (
                    <div style={{
                      marginTop: 8, padding: '8px 10px',
                      background: 'rgba(255,255,255,0.7)',
                      borderRadius: 8, fontSize: 12, color: '#475569',
                      borderLeft: `3px solid ${ac.border}`
                    }}>
                      💡 {alert.catchup_plan.advice}
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Weak topics & recent quizzes row */}
      {(weak_topics?.length > 0 || recent_quizzes?.length > 0) && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>

          {/* Weak topics */}
          {weak_topics?.length > 0 && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h2 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: '#1e293b' }}>
                  🎯 Weak Topics
                </h2>
                <button onClick={() => navigate('/analytics')} style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontSize: 12, color: '#6366f1', fontWeight: 600
                }}>View all →</button>
              </div>
              <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, overflow: 'hidden' }}>
                {weak_topics.map((t, i) => (
                  <div key={i} style={{
                    padding: '10px 14px',
                    borderBottom: i < weak_topics.length - 1 ? '1px solid #f1f5f9' : 'none'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 13, color: '#1e293b' }}>{t.topic_name}</div>
                        <div style={{ fontSize: 11, color: '#94a3b8' }}>{t.subject_name}</div>
                      </div>
                      <span style={{
                        fontSize: 13, fontWeight: 700,
                        color: t.mastery_score < 40 ? '#ef4444' : t.mastery_score < 65 ? '#f59e0b' : '#10b981'
                      }}>
                        {t.mastery_score?.toFixed(0) || 0}%
                      </span>
                    </div>
                    <ScoreBar score={t.mastery_score || 0} height={4} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent quizzes */}
          {recent_quizzes?.length > 0 && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h2 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: '#1e293b' }}>
                  ✏️ Recent Quizzes
                </h2>
                <button onClick={() => navigate('/quiz')} style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontSize: 12, color: '#6366f1', fontWeight: 600
                }}>Take quiz →</button>
              </div>
              <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 14, overflow: 'hidden' }}>
                {recent_quizzes.slice(0, 5).map((q, i) => (
                  <div key={i} style={{
                    padding: '10px 14px', display: 'flex',
                    justifyContent: 'space-between', alignItems: 'center',
                    borderBottom: i < 4 ? '1px solid #f1f5f9' : 'none'
                  }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 13, color: '#1e293b' }}>{q.topic_name}</div>
                      <div style={{ fontSize: 11, color: '#94a3b8' }}>
                        {q.subject_name} · {new Date(q.timestamp).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                      </div>
                    </div>
                    <span style={{
                      fontSize: 14, fontWeight: 800,
                      color: q.score >= 75 ? '#10b981' : q.score >= 50 ? '#f59e0b' : '#ef4444'
                    }}>
                      {q.score?.toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}