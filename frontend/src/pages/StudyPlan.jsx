import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

const STREAMS = ['PCM', 'PCB', 'Commerce', 'Arts', 'University']

const ALERT_COLORS = {
  critical: { bg:'#fef2f2', border:'#fca5a5', text:'#dc2626', badge:'#fee2e2' },
  warning:  { bg:'#fffbeb', border:'#fcd34d', text:'#d97706', badge:'#fef3c7' },
  safe:     { bg:'#f0fdf4', border:'#86efac', text:'#16a34a', badge:'#dcfce7' }
}

export default function StudyPlan({ user }) {
  const [subjects,    setSubjects]    = useState([])
  const [plan,        setPlan]        = useState(null)
  const [loading,     setLoading]     = useState(false)
  const [error,       setError]       = useState('')
  const [activeTab,   setActiveTab]   = useState('plan')   // plan | backlog
  const [selSubject,  setSelSubject]  = useState('')
  const [examDate,    setExamDate]    = useState('')
  const [examName,    setExamName]    = useState('')
  const [generating,  setGenerating]  = useState(false)

  useEffect(() => {
    fetchSubjects()
  }, [])

  const fetchSubjects = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API}/subjects/${user.user_id}`)
      setSubjects(res.data.subjects)
    } catch { setError('Could not load subjects') }
    finally { setLoading(false) }
  }

  const generatePlan = async () => {
    if (!selSubject || !examDate) {
      setError('Please select a subject and exam date'); return
    }
    setGenerating(true); setError(''); setPlan(null)
    try {
      const res = await axios.post(`${API}/study-plan/${user.user_id}`, {
        subject_id: parseInt(selSubject),
        exam_date:  examDate,
        exam_name:  examName || 'Exam'
      })
      setPlan(res.data)
      setActiveTab('plan')
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to generate plan')
    } finally { setGenerating(false) }
  }

  const subj = subjects.find(s => s.id === parseInt(selSubject))

  return (
    <div>
      <div style={{ marginBottom:24 }}>
        <h1 style={{ fontSize:24, fontWeight:800, color:'#1e293b' }}>
          Study Plan
        </h1>
        <p style={{ color:'#64748b', fontSize:14, marginTop:4 }}>
          AI-generated daily schedule based on topic difficulty and your exam date
        </p>
      </div>

      {/* Setup card */}
      <div style={{ background:'#fff', border:'1.5px solid #e2e8f0',
        borderRadius:16, padding:'1.5rem', marginBottom:24,
        boxShadow:'0 2px 8px rgba(0,0,0,0.05)' }}>
        <h2 style={{ fontSize:15, fontWeight:700, color:'#1e293b', marginBottom:16 }}>
          Configure your plan
        </h2>

        {error && (
          <div style={{ background:'#fef2f2', color:'#dc2626', padding:'10px 14px',
            borderRadius:8, fontSize:13, marginBottom:14 }}>{error}</div>
        )}

        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr auto', gap:12, alignItems:'end' }}>
          <div>
            <label style={{ fontSize:12, fontWeight:600, color:'#374151',
              display:'block', marginBottom:6 }}>Subject</label>
            <select value={selSubject} onChange={e => setSelSubject(e.target.value)}
              style={{ width:'100%', padding:'10px 12px', border:'1.5px solid #e2e8f0',
                borderRadius:10, fontSize:14, background:'#fff', outline:'none' }}>
              <option value=''>Select subject...</option>
              {subjects.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize:12, fontWeight:600, color:'#374151',
              display:'block', marginBottom:6 }}>Exam name</label>
            <input value={examName} onChange={e => setExamName(e.target.value)}
              placeholder='e.g. JEE Mains 2026'
              style={{ width:'100%', padding:'10px 12px', border:'1.5px solid #e2e8f0',
                borderRadius:10, fontSize:14, outline:'none' }} />
          </div>

          <div>
            <label style={{ fontSize:12, fontWeight:600, color:'#374151',
              display:'block', marginBottom:6 }}>Exam date</label>
            <input type='date' value={examDate} onChange={e => setExamDate(e.target.value)}
              style={{ width:'100%', padding:'10px 12px', border:'1.5px solid #e2e8f0',
                borderRadius:10, fontSize:14, outline:'none' }} />
          </div>

          <button onClick={generatePlan} disabled={generating || !selSubject || !examDate}
            style={{ padding:'10px 20px',
              background: (generating || !selSubject || !examDate) ? '#c7d2fe' : '#6366f1',
              color:'#fff', border:'none', borderRadius:10,
              fontSize:14, fontWeight:600, cursor:'pointer', whiteSpace:'nowrap' }}>
            {generating ? 'Generating...' : 'Generate Plan'}
          </button>
        </div>

        {subj && examDate && (
          <div style={{ marginTop:14, padding:'10px 14px', background:'#f8fafc',
            borderRadius:8, fontSize:13, color:'#475569', display:'flex', gap:20 }}>
            <span>📚 {subj.chapters_total} topics</span>
            <span>📅 {daysUntil(examDate)} days until exam</span>
            <span>🎯 {subj.exam_name || examName || 'Exam'}</span>
          </div>
        )}
      </div>

      {/* Plan output */}
      {plan && (
        <div>
          {/* Summary stats */}
          <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:20 }}>
            {[
              { label:'Days to exam',    value: plan.days_to_exam,           color:'#6366f1' },
              { label:'Topics total',    value: plan.total_topics,           color:'#0ea5e9' },
              { label:'Topics/day',      value: plan.topics_per_day,         color:'#16a34a' },
              { label:'Backlog risk',    value: plan.backlog_severity + '/10', color: plan.backlog_severity >= 7 ? '#dc2626' : plan.backlog_severity >= 4 ? '#d97706' : '#16a34a' },
            ].map(s => (
              <div key={s.label} style={{ background:'#fff', border:'1.5px solid #e2e8f0',
                borderRadius:12, padding:'1rem 1.25rem',
                boxShadow:'0 1px 4px rgba(0,0,0,0.05)' }}>
                <div style={{ fontSize:26, fontWeight:800, color:s.color }}>{s.value}</div>
                <div style={{ fontSize:12, color:'#64748b', marginTop:4 }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Tabs */}
          <div style={{ display:'flex', gap:4, marginBottom:16,
            background:'#f1f5f9', borderRadius:10, padding:4, width:'fit-content' }}>
            {['plan','backlog'].map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                style={{ padding:'8px 20px', borderRadius:8, border:'none',
                  cursor:'pointer', fontSize:13, fontWeight:600,
                  background: activeTab===tab ? '#fff' : 'transparent',
                  color: activeTab===tab ? '#6366f1' : '#64748b',
                  boxShadow: activeTab===tab ? '0 1px 4px rgba(0,0,0,0.1)' : 'none' }}>
                {tab === 'plan' ? '📅 Daily Schedule' : '⚠️ Backlog Tracker'}
              </button>
            ))}
          </div>

          {/* Daily schedule */}
          {activeTab === 'plan' && (
            <div>
              <p style={{ fontSize:13, color:'#64748b', marginBottom:16 }}>
                {plan.message}
              </p>
              <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
                {plan.daily_schedule.map((day, i) => (
                  <DayCard key={i} day={day} index={i} />
                ))}
              </div>
              {plan.daily_schedule.length === 0 && (
                <div style={{ textAlign:'center', padding:'2rem', color:'#94a3b8' }}>
                  No schedule generated. Check your exam date.
                </div>
              )}
            </div>
          )}

          {/* Backlog tracker */}
          {activeTab === 'backlog' && (
            <BacklogView plan={plan} />
          )}
        </div>
      )}

      {!plan && !generating && (
        <div style={{ textAlign:'center', padding:'4rem 2rem',
          background:'#fff', border:'1.5px dashed #e2e8f0', borderRadius:16,
          color:'#94a3b8' }}>
          <div style={{ fontSize:48, marginBottom:12 }}>📅</div>
          <div style={{ fontSize:15, fontWeight:600, color:'#64748b' }}>
            Select a subject and exam date to generate your study plan
          </div>
          <div style={{ fontSize:13, marginTop:6 }}>
            The AI will create a day-by-day schedule based on topic difficulty
          </div>
        </div>
      )}
    </div>
  )
}

function DayCard({ day, index }) {
  const [open, setOpen] = useState(index < 7)
  const isToday = day.is_today
  const isPast  = day.is_past

  return (
    <div style={{
      background: isToday ? '#eef2ff' : isPast ? '#f8fafc' : '#fff',
      border:`1.5px solid ${isToday ? '#6366f1' : isPast ? '#e2e8f0' : '#e2e8f0'}`,
      borderRadius:12, overflow:'hidden',
      opacity: isPast ? 0.7 : 1
    }}>
      <div onClick={() => setOpen(o => !o)}
        style={{ padding:'12px 16px', cursor:'pointer',
          display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div style={{ display:'flex', alignItems:'center', gap:12 }}>
          <div style={{
            width:36, height:36, borderRadius:10, flexShrink:0,
            background: isToday ? '#6366f1' : isPast ? '#e2e8f0' : '#f1f5f9',
            color: isToday ? '#fff' : '#64748b',
            display:'flex', alignItems:'center', justifyContent:'center',
            fontSize:12, fontWeight:700
          }}>
            {isPast ? '✓' : `D${day.day_number}`}
          </div>
          <div>
            <div style={{ fontWeight:600, fontSize:14,
              color: isToday ? '#3730a3' : '#1e293b' }}>
              {day.date_label}
              {isToday && <span style={{ marginLeft:8, fontSize:11,
                background:'#6366f1', color:'#fff', padding:'2px 8px',
                borderRadius:99 }}>TODAY</span>}
            </div>
            <div style={{ fontSize:12, color:'#64748b', marginTop:1 }}>
              {day.topics.length} topic{day.topics.length !== 1 ? 's' : ''} ·{' '}
              ~{day.estimated_minutes} min
            </div>
          </div>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <div style={{ display:'flex', gap:3 }}>
            {day.topics.slice(0,4).map((t,i) => (
              <div key={i} style={{
                width:8, height:8, borderRadius:99,
                background: diffColor(t.difficulty)
              }} />
            ))}
          </div>
          <span style={{ fontSize:12, color:'#94a3b8' }}>{open ? '▲' : '▼'}</span>
        </div>
      </div>

      {open && (
        <div style={{ borderTop:'1px solid #e2e8f0', padding:'12px 16px' }}>
          {day.topics.map((t, i) => (
            <div key={i} style={{ display:'flex', alignItems:'center',
              gap:10, padding:'6px 0',
              borderBottom: i < day.topics.length-1 ? '1px solid #f1f5f9' : 'none' }}>
              <div style={{
                width:6, height:6, borderRadius:99, flexShrink:0,
                background: diffColor(t.difficulty)
              }} />
              <div style={{ flex:1, fontSize:13, color:'#374151' }}>{t.name}</div>
              <span style={{
                fontSize:10, fontWeight:600, padding:'2px 7px', borderRadius:99,
                background: diffBg(t.difficulty), color: diffColor(t.difficulty)
              }}>
                {diffLabel(t.difficulty)}
              </span>
              <span style={{ fontSize:11, color:'#94a3b8' }}>~{t.minutes}m</span>
            </div>
          ))}
          {day.note && (
            <div style={{ marginTop:10, padding:'8px 10px', background:'#fffbeb',
              borderRadius:8, fontSize:12, color:'#92400e' }}>
              💡 {day.note}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function BacklogView({ plan }) {
  const ac = ALERT_COLORS[plan.alert_level] || ALERT_COLORS.safe

  return (
    <div>
      {/* Backlog status */}
      <div style={{ background:ac.bg, border:`1.5px solid ${ac.border}`,
        borderRadius:16, padding:'1.5rem', marginBottom:20 }}>
        <div style={{ display:'flex', justifyContent:'space-between',
          alignItems:'flex-start', marginBottom:12 }}>
          <div>
            <h3 style={{ fontSize:16, fontWeight:700, color:ac.text }}>
              {plan.alert_level === 'critical' ? '🚨 Critical Backlog Risk'
               : plan.alert_level === 'warning' ? '⚠️ Backlog Warning'
               : '✅ On Track'}
            </h3>
            <p style={{ fontSize:13, color:'#475569', marginTop:4, lineHeight:1.6 }}>
              {plan.backlog_message}
            </p>
          </div>
          <span style={{ background:ac.badge, color:ac.text,
            fontSize:14, fontWeight:800, padding:'6px 14px',
            borderRadius:99, whiteSpace:'nowrap' }}>
            {plan.backlog_severity}/10
          </span>
        </div>

        {/* Severity bar */}
        <div style={{ height:8, background:'rgba(0,0,0,0.08)', borderRadius:99 }}>
          <div style={{
            height:'100%', borderRadius:99,
            width:`${plan.backlog_severity * 10}%`,
            background:ac.text, transition:'width 0.6s ease'
          }} />
        </div>
      </div>

      {/* Topics at risk */}
      {plan.at_risk_topics && plan.at_risk_topics.length > 0 && (
        <div style={{ marginBottom:20 }}>
          <h3 style={{ fontSize:14, fontWeight:700, color:'#1e293b', marginBottom:12 }}>
            Topics at risk (high difficulty, not yet scheduled)
          </h3>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(200px,1fr))', gap:8 }}>
            {plan.at_risk_topics.map((t, i) => (
              <div key={i} style={{ background:'#fef2f2', border:'1px solid #fca5a5',
                borderRadius:10, padding:'10px 12px' }}>
                <div style={{ fontSize:13, fontWeight:600, color:'#1e293b' }}>{t.name}</div>
                <div style={{ fontSize:11, color:'#dc2626', marginTop:3 }}>
                  Difficulty {t.difficulty}/5 · Day {t.scheduled_day}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Catch-up advice */}
      {plan.catchup_advice && (
        <div style={{ background:'#fff', border:'1.5px solid #e2e8f0',
          borderRadius:12, padding:'1.25rem' }}>
          <h3 style={{ fontSize:14, fontWeight:700, color:'#1e293b', marginBottom:10 }}>
            Catch-up recommendations
          </h3>
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {plan.catchup_advice.map((tip, i) => (
              <div key={i} style={{ display:'flex', gap:10, alignItems:'flex-start' }}>
                <div style={{ width:20, height:20, borderRadius:6, background:'#eef2ff',
                  color:'#6366f1', display:'flex', alignItems:'center',
                  justifyContent:'center', fontSize:11, fontWeight:700, flexShrink:0 }}>
                  {i+1}
                </div>
                <div style={{ fontSize:13, color:'#475569', lineHeight:1.5 }}>{tip}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function daysUntil(dateStr) {
  return Math.max(0, Math.ceil((new Date(dateStr) - new Date()) / 86400000))
}
function diffColor(d) {
  if (d >= 4.5) return '#7c3aed'
  if (d >= 4)   return '#dc2626'
  if (d >= 3)   return '#d97706'
  return '#16a34a'
}
function diffBg(d) {
  if (d >= 4.5) return '#f5f3ff'
  if (d >= 4)   return '#fef2f2'
  if (d >= 3)   return '#fffbeb'
  return '#f0fdf4'
}
function diffLabel(d) {
  if (d >= 4.5) return 'Expert'
  if (d >= 4)   return 'Hard'
  if (d >= 3)   return 'Medium'
  return 'Easy'
}
