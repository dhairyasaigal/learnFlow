import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell, Legend
} from 'recharts'

const API = 'http://localhost:8000'

const SUBJECT_COLORS = [
  '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6',
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#84cc16'
]

function StatusBadge({ status }) {
  const styles = {
    lstm:               { bg: '#f0fdf4', color: '#16a34a', text: '🤖 ML Model' },
    rule_based_fallback:{ bg: '#fef3c7', color: '#d97706', text: '📐 Rule-based' }
  }
  const s = styles[status] || styles.rule_based_fallback
  return (
    <span style={{
      background: s.bg, color: s.color, fontSize: 11, fontWeight: 600,
      padding: '2px 8px', borderRadius: 99, border: `1px solid ${s.color}33`
    }}>{s.text}</span>
  )
}

function StatCard({ label, value, sub, color = '#6366f1', prefix = '' }) {
  return (
    <div style={{
      background: '#f8fafc', padding: 20, borderRadius: 14,
      border: '1px solid #e2e8f0'
    }}>
      <div style={{ fontSize: 12, color: '#64748b', fontWeight: 700, letterSpacing: '0.05em' }}>
        {label}
      </div>
      <div style={{ fontSize: 32, fontWeight: 800, color, marginTop: 8 }}>
        {prefix}{value}
      </div>
      {sub && <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>{sub}</div>}
    </div>
  )
}

function InsufficientDataCard({ label, current, required, message }) {
  const pct = Math.min(100, (current / required) * 100)
  return (
    <div style={{
      background: '#f8fafc', padding: 20, borderRadius: 14,
      border: '1px dashed #cbd5e1'
    }}>
      <div style={{ fontSize: 12, color: '#64748b', fontWeight: 700, letterSpacing: '0.05em' }}>
        {label}
      </div>
      <div style={{
        fontSize: 16, fontWeight: 700, color: '#94a3b8', marginTop: 8
      }}>Insufficient data</div>
      <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>{message}</div>
      <div style={{
        height: 6, background: '#e2e8f0', borderRadius: 99, marginTop: 10, overflow: 'hidden'
      }}>
        <div style={{
          width: `${pct}%`, height: '100%',
          background: '#6366f1', borderRadius: 99,
          transition: 'width 0.5s ease'
        }} />
      </div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
        {current} / {required} quizzes
      </div>
    </div>
  )
}

export default function Analytics({ user }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    setLoading(true)
    axios.get(`${API}/analytics/${user.user_id}`)
      .then(r => { setData(r.data); setLoading(false) })
      .catch(e => { setError('Failed to load analytics'); setLoading(false) })
  }, [user.user_id])

  if (loading) return (
    <div style={{ padding: 60, textAlign: 'center', color: '#64748b' }}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>📊</div>
      <div>Loading your analytics...</div>
    </div>
  )

  if (error) return (
    <div style={{ padding: 40, textAlign: 'center', color: '#ef4444' }}>
      {error}
    </div>
  )

  const modelStatus  = data?.model_status || {}
  const heatmap      = data?.heatmap || []
  const curves       = data?.retention_curves || []
  const mastery      = data?.mastery_breakdown || []
  const recentPerf   = data?.recent_performance || []
  const examPred     = data?.exam_prediction || {}

  // Build performance trend (last 10 quizzes in chronological order)
  const trendData = [...recentPerf].reverse().slice(-10).map((a, i) => ({
    index:   i + 1,
    score:   a.score,
    topic:   a.topic_name,
    subject: a.subject_name
  }))

  return (
    <div style={{ paddingBottom: 80 }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1e293b', margin: 0 }}>
          📊 Learning Analytics
        </h1>
        <p style={{ color: '#64748b', margin: '6px 0 0' }}>
          Powered by your real study data — no fake predictions.
        </p>
      </div>

      {/* Model status banner */}
      <div style={{
        background: '#fff', border: '1px solid #e2e8f0',
        borderRadius: 12, padding: '12px 16px', marginBottom: 24,
        display: 'flex', gap: 20, alignItems: 'center', flexWrap: 'wrap'
      }}>
        <span style={{ fontSize: 13, color: '#475569', fontWeight: 600 }}>Prediction engine:</span>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 13, color: '#64748b' }}>
            <span>Forgetting model:</span>
            <StatusBadge status={modelStatus.forgetting_model} />
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 13, color: '#64748b' }}>
            <span>Backlog model:</span>
            <StatusBadge status={modelStatus.backlog_model} />
          </div>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 28 }}>
        {/* Exam prediction — honest, data-driven */}
        {examPred.status === 'available' ? (
          <StatCard
            label="ESTIMATED EXAM SCORE"
            value={`${examPred.estimated_score}%`}
            sub={examPred.note}
            color="#10b981"
          />
        ) : (
          <InsufficientDataCard
            label="EXAM SCORE PREDICTION"
            current={examPred.data_points || 0}
            required={examPred.required || 10}
            message={examPred.note}
          />
        )}
        <StatCard
          label="TOPICS REVIEWED"
          value={curves.length}
          sub="Topics with spaced repetition schedules"
          color="#6366f1"
        />
        <StatCard
          label="SUBJECTS TRACKED"
          value={heatmap.length}
          sub="Subjects with quiz data"
          color="#f59e0b"
        />
        <StatCard
          label="RECENT QUIZZES"
          value={recentPerf.length}
          sub="Stored performance records"
          color="#3b82f6"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        {/* Retention / Forgetting Curves */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <h2 style={{ fontSize: 17, fontWeight: 700, margin: 0, color: '#1e293b' }}>
              🧠 Forgetting Curves
            </h2>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>Ebbinghaus decay from current recall</span>
          </div>
          <div style={{
            background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 14, padding: 16
          }}>
            {curves.length === 0 ? (
              <div style={{ padding: '24px 0', textAlign: 'center', color: '#94a3b8', fontSize: 14 }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>📈</div>
                Complete quizzes to generate forgetting curves.
              </div>
            ) : (
              curves.map(curve => (
                <div key={curve.topic} style={{ marginBottom: 24 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>{curve.topic}</span>
                    <span style={{
                      fontSize: 11, fontWeight: 600,
                      color: curve.urgency === 'today' ? '#ef4444' : curve.urgency === 'soon' ? '#f59e0b' : '#10b981',
                      background: curve.urgency === 'today' ? '#fef2f2' : curve.urgency === 'soon' ? '#fffbeb' : '#f0fdf4',
                      padding: '2px 8px', borderRadius: 99
                    }}>
                      {curve.urgency?.toUpperCase()} — {curve.current_recall}% recall
                    </span>
                  </div>
                  <div style={{ height: 140 }}>
                    <ResponsiveContainer>
                      <LineChart data={curve.curve} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="day" style={{ fontSize: 10 }} tickLine={false} axisLine={false}
                          tickFormatter={v => `Day ${v}`} />
                        <YAxis domain={[0, 100]} style={{ fontSize: 10 }} tickLine={false} axisLine={false}
                          tickFormatter={v => `${v}%`} />
                        <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }}
                          formatter={v => [`${v}%`, 'Recall']} />
                        <Line type="monotone" dataKey="recall" stroke="#f43f5e" strokeWidth={2.5}
                          dot={{ r: 3 }} activeDot={{ r: 5 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Subject Performance Heatmap — REAL data */}
        <div>
          <div style={{ marginBottom: 14 }}>
            <h2 style={{ fontSize: 17, fontWeight: 700, margin: 0, color: '#1e293b' }}>
              📚 Subject Proficiency
            </h2>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>Real average from your quiz attempts</span>
          </div>
          <div style={{
            background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 14, padding: 16, height: 320
          }}>
            {heatmap.length === 0 ? (
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#94a3b8', fontSize: 14 }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>🎯</div>
                Take quizzes to see your subject proficiency.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={heatmap} margin={{ top: 4, right: 4, left: -20, bottom: 28 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="subject" style={{ fontSize: 10 }} tickLine={false}
                    axisLine={false} angle={-35} textAnchor="end" interval={0} />
                  <YAxis domain={[0, 100]} style={{ fontSize: 10 }} tickLine={false}
                    axisLine={false} tickFormatter={v => `${v}%`} />
                  <Tooltip
                    cursor={{ fill: '#f8fafc' }}
                    contentStyle={{ borderRadius: 8, fontSize: 12 }}
                    formatter={(v, n, p) => [
                      `${v}% avg (${p.payload.attempts} quizzes)`,
                      'Proficiency'
                    ]}
                  />
                  <Bar dataKey="score" radius={[5, 5, 0, 0]}>
                    {heatmap.map((_, i) => (
                      <Cell key={i}
                        fill={SUBJECT_COLORS[i % SUBJECT_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Performance Trend */}
      {trendData.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ marginBottom: 14 }}>
            <h2 style={{ fontSize: 17, fontWeight: 700, margin: 0, color: '#1e293b' }}>
              📈 Recent Quiz Performance
            </h2>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>Last {trendData.length} quizzes (oldest → newest)</span>
          </div>
          <div style={{
            background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 14, padding: 16, height: 220
          }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 4, right: 20, bottom: 4, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="index" style={{ fontSize: 10 }} tickLine={false} axisLine={false}
                  tickFormatter={v => `Quiz ${v}`} />
                <YAxis domain={[0, 100]} style={{ fontSize: 10 }} tickLine={false} axisLine={false}
                  tickFormatter={v => `${v}%`} />
                <Tooltip
                  contentStyle={{ borderRadius: 8, fontSize: 12 }}
                  formatter={v => [`${v}%`, 'Score']}
                  labelFormatter={(_, payload) =>
                    payload?.[0]?.payload?.topic || ''
                  }
                />
                <Line type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={2.5}
                  dot={{ r: 4, fill: '#6366f1' }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Topic Mastery Table */}
      {mastery.length > 0 && (
        <div>
          <div style={{ marginBottom: 14 }}>
            <h2 style={{ fontSize: 17, fontWeight: 700, margin: 0, color: '#1e293b' }}>
              🎯 Topic Mastery
            </h2>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>Sorted by weakest topics first</span>
          </div>
          <div style={{
            background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 14, overflow: 'hidden'
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                  {['Topic', 'Subject', 'Mastery', 'Last Score', 'Accuracy', 'Attempts'].map(h => (
                    <th key={h} style={{
                      padding: '10px 14px', textAlign: 'left',
                      fontSize: 11, fontWeight: 700, color: '#64748b',
                      letterSpacing: '0.04em'
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {mastery.slice(0, 10).map((t, i) => {
                  const mastery_pct = t.mastery_score || 0
                  const mastery_color = mastery_pct >= 75 ? '#10b981' : mastery_pct >= 50 ? '#f59e0b' : '#ef4444'
                  return (
                    <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '10px 14px', fontWeight: 500, color: '#374151' }}>
                        {t.topic_name}
                      </td>
                      <td style={{ padding: '10px 14px', color: '#64748b' }}>
                        {t.subject_name}
                      </td>
                      <td style={{ padding: '10px 14px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{
                            flex: 1, height: 6, background: '#f1f5f9',
                            borderRadius: 99, overflow: 'hidden'
                          }}>
                            <div style={{
                              width: `${mastery_pct}%`, height: '100%',
                              background: mastery_color, borderRadius: 99
                            }} />
                          </div>
                          <span style={{ fontSize: 12, color: mastery_color, fontWeight: 600 }}>
                            {mastery_pct.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '10px 14px', color: '#374151' }}>
                        {(t.last_quiz_score || 0).toFixed(0)}%
                      </td>
                      <td style={{ padding: '10px 14px', color: '#374151' }}>
                        {((t.accuracy_rate || 0) * 100).toFixed(0)}%
                      </td>
                      <td style={{ padding: '10px 14px', color: '#94a3b8' }}>
                        {t.attempts_count || 0}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {heatmap.length === 0 && mastery.length === 0 && curves.length === 0 && (
        <div style={{
          textAlign: 'center', padding: '60px 20px',
          background: '#fff', borderRadius: 14,
          border: '1px solid #e2e8f0', color: '#94a3b8'
        }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
          <h3 style={{ margin: '0 0 8px', color: '#374151', fontWeight: 700 }}>
            No analytics data yet
          </h3>
          <p style={{ margin: 0, fontSize: 14 }}>
            Take some quizzes and log study sessions — your real analytics will appear here.
          </p>
        </div>
      )}
    </div>
  )
}
