import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

const DIFF_LABEL = { 1:'Easy', 2:'Easy', 3:'Medium', 4:'Hard', 5:'Expert' }
const DIFF_COLOR = {
  1:'#16a34a', 2:'#16a34a', 3:'#d97706', 4:'#dc2626', 5:'#7c3aed'
}
const DIFF_BG = {
  1:'#f0fdf4', 2:'#f0fdf4', 3:'#fffbeb', 4:'#fef2f2', 5:'#f5f3ff'
}

export default function Quiz({ user }) {
  const [phase,      setPhase]      = useState('subject')   // subject|topic|quiz|result
  const [subjects,   setSubjects]   = useState([])
  const [topics,     setTopics]     = useState([])
  const [questions,  setQuestions]  = useState([])
  const [selSubject, setSelSubject] = useState(null)
  const [selTopic,   setSelTopic]   = useState(null)
  const [current,    setCurrent]    = useState(0)
  const [answers,    setAnswers]    = useState({})
  const [result,     setResult]     = useState(null)
  const [rating,     setRating]     = useState(3)
  const [startTime,  setStartTime]  = useState(null)
  const [elapsed,    setElapsed]    = useState(0)
  const [notes,      setNotes]      = useState({})
  const [loading,    setLoading]    = useState(false)
  const [xpEarned,   setXpEarned]   = useState(0)

  useEffect(() => {
    let intv
    if (phase === 'quiz' && startTime) {
      intv = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startTime) / 1000))
      }, 1000)
    }
    return () => clearInterval(intv)
  }, [phase, startTime])

  useEffect(() => {
    const stream = user.stream || 'PCM'
    Promise.all([
      axios.get(`${API}/subjects/${user.user_id}`),
      axios.get(`${API}/curriculum/${stream}`)
    ]).then(([r1, r2]) => {
      const validKeys = Object.keys(r2.data.subjects)
      setSubjects(r1.data.subjects.filter(s => validKeys.includes(s.name)))
    }).catch(e => console.error(e))
  }, [])

  const pickSubject = async (subj) => {
    setSelSubject(subj)
    setLoading(true)
    try {
      const res = await axios.get(`${API}/topics/${subj.id}`)
      setTopics(res.data.topics)
      setPhase('topic')
    } catch { alert('Failed to load topics') }
    finally { setLoading(false) }
  }

  const startQuiz = async (topic) => {
    setSelTopic(topic)
    setLoading(true)
    try {
      const res = await axios.get(`${API}/quiz/${topic.id}/questions`)
      setQuestions(res.data.questions)
      setAnswers({})
      setNotes({})
      setCurrent(0)
      setResult(null)
      setStartTime(Date.now())
      setElapsed(0)
      setPhase('quiz')
    } catch {
      alert('No questions available for this topic yet. Check back soon!')
    } finally { setLoading(false) }
  }

  const selectAnswer = (qId, opt) => {
    if (result) return
    setAnswers(prev => ({ ...prev, [qId]: opt }))
  }

  const submitQuiz = async () => {
    const timeMins = (Date.now() - startTime) / 60000
    let score = 0, correct = 0, checkResults = {}
    try {
      const r = await axios.post(`${API}/quiz/check/${selTopic.id}`, { answers })
      score = r.data.score; correct = r.data.correct; checkResults = r.data.results
    } catch (e) { console.error(e) }

    setResult({ score, correct, total: questions.length, results: checkResults })

    try {
      const r2 = await axios.post(`${API}/quiz/submit/${user.user_id}`, {
        topic_id: selTopic.id, score, time_spent: timeMins,
        self_rating: rating, difficulty: Math.round(selTopic.difficulty)
      })
      setXpEarned(r2.data.xp_earned || 0)
    } catch (e) { console.error(e) }
    setPhase('result')
  }

  const reset = () => {
    setPhase('subject'); setSelSubject(null); setSelTopic(null)
    setQuestions([]); setAnswers({}); setNotes({}); setResult(null); setTopics([])
  }

  const q = questions[current]
  const answered = Object.keys(answers).length
  const progress = questions.length ? (answered / questions.length) * 100 : 0

  // ── Subject selection ──────────────────────────────────────
  if (phase === 'subject') return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, color: '#1e293b' }}>
          Quiz
        </h1>
        <p style={{ color: '#64748b', fontSize: 14, marginTop: 4 }}>
          Pick a subject to test your knowledge
        </p>
      </div>

      {subjects.length === 0 ? (
        <div style={{ textAlign:'center', padding:'3rem', color:'#94a3b8' }}>
          No subjects found. Add subjects first.
        </div>
      ) : (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(200px, 1fr))', gap:16 }}>
          {subjects.map(s => (
            <button key={s.id} onClick={() => pickSubject(s)}
              disabled={loading}
              style={{
                background:'#fff', border:'1.5px solid #e2e8f0',
                borderRadius:16, padding:'1.5rem 1.25rem',
                cursor:'pointer', textAlign:'left',
                transition:'all 0.15s',
                boxShadow:'0 1px 3px rgba(0,0,0,0.06)'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = '#6366f1'
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(99,102,241,0.15)'
                e.currentTarget.style.transform = 'translateY(-2px)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = '#e2e8f0'
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.06)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}>
              <div style={{ fontSize:28, marginBottom:10 }}>
                {subjectEmoji(s.name)}
              </div>
              <div style={{ fontWeight:700, fontSize:15, color:'#1e293b' }}>
                {s.name}
              </div>
              <div style={{ fontSize:12, color:'#94a3b8', marginTop:4 }}>
                {s.stream} · {s.chapters_total} topics
              </div>
              {s.exam_name && (
                <div style={{ fontSize:11, color:'#6366f1', marginTop:6,
                  background:'#eef2ff', padding:'2px 8px', borderRadius:99,
                  display:'inline-block' }}>
                  {s.exam_name}
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )

  // ── Topic selection ────────────────────────────────────────
  if (phase === 'topic') return (
    <div>
      <div style={{ display:'flex', alignItems:'center', gap:12, marginBottom:24 }}>
        <button onClick={() => setPhase('subject')}
          style={{ background:'#f1f5f9', border:'none', borderRadius:8,
            padding:'8px 14px', cursor:'pointer', fontSize:13, color:'#475569' }}>
          ← Back
        </button>
        <div>
          <h1 style={{ fontSize:20, fontWeight:800, color:'#1e293b' }}>
            {subjectEmoji(selSubject.name)} {selSubject.name}
          </h1>
          <p style={{ color:'#64748b', fontSize:13, marginTop:2 }}>
            Choose a topic to quiz yourself on
          </p>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(220px, 1fr))', gap:12 }}>
        {topics.map(t => {
          const d = Math.round(t.difficulty)
          return (
            <button key={t.id} onClick={() => startQuiz(t)}
              disabled={loading}
              style={{
                background:'#fff', border:'1.5px solid #e2e8f0',
                borderRadius:14, padding:'1.25rem',
                cursor:'pointer', textAlign:'left',
                transition:'all 0.15s',
                boxShadow:'0 1px 3px rgba(0,0,0,0.05)'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = DIFF_COLOR[d]
                e.currentTarget.style.boxShadow = `0 4px 14px ${DIFF_COLOR[d]}22`
                e.currentTarget.style.transform = 'translateY(-2px)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = '#e2e8f0'
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.05)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}>
              <div style={{ display:'flex', justifyContent:'space-between',
                alignItems:'flex-start', marginBottom:8 }}>
                <div style={{ fontWeight:600, fontSize:14, color:'#1e293b',
                  lineHeight:1.4, flex:1, marginRight:8 }}>
                  {t.name}
                </div>
                <span style={{
                  background: DIFF_BG[d], color: DIFF_COLOR[d],
                  fontSize:10, fontWeight:700, padding:'2px 7px',
                  borderRadius:99, whiteSpace:'nowrap'
                }}>
                  {DIFF_LABEL[d]}
                </span>
              </div>
              <div style={{ display:'flex', gap:4, marginTop:6 }}>
                {[1,2,3,4,5].map(i => (
                  <div key={i} style={{
                    flex:1, height:3, borderRadius:99,
                    background: i <= d ? DIFF_COLOR[d] : '#e2e8f0'
                  }} />
                ))}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )

  // ── Quiz in progress ───────────────────────────────────────
  if (phase === 'quiz' && q) return (
    <div style={{ maxWidth:640, margin:'0 auto' }}>
      {/* Header */}
      <div style={{ display:'flex', justifyContent:'space-between',
        alignItems:'center', marginBottom:20 }}>
        <div>
          <div style={{ fontSize:13, color:'#64748b' }}>
            {selSubject.name} · {selTopic.name}
          </div>
          <div style={{ fontSize:12, color:'#94a3b8', marginTop:2 }}>
            Question {current + 1} of {questions.length}
          </div>
        </div>
        <div style={{ textAlign:'right', display:'flex', flexDirection:'column', alignItems:'flex-end' }}>
          <div style={{ fontSize:13, fontWeight:600, color:'#6366f1' }}>
            {answered}/{questions.length} answered
          </div>
          <div style={{ fontSize:13, fontWeight:700, color:'#475569', marginTop:4, background:'#f1f5f9', padding:'2px 8px', borderRadius:8 }}>
            ⏱ {Math.floor(elapsed / 60).toString().padStart(2, '0')}:{(elapsed % 60).toString().padStart(2, '0')}
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div style={{ height:6, background:'#f1f5f9', borderRadius:99, marginBottom:24 }}>
        <div style={{
          height:'100%', borderRadius:99, background:'#6366f1',
          width:`${progress}%`, transition:'width 0.3s ease'
        }} />
      </div>

      {/* Question dots */}
      <div style={{ display:'flex', gap:6, marginBottom:20, flexWrap:'wrap' }}>
        {questions.map((qq, i) => (
          <button key={i} onClick={() => setCurrent(i)} style={{
            width:32, height:32, borderRadius:8, border:'none',
            cursor:'pointer', fontSize:12, fontWeight:600,
            background: i === current ? '#6366f1'
              : answers[qq.id] ? '#e0e7ff' : '#f1f5f9',
            color: i === current ? '#fff'
              : answers[qq.id] ? '#6366f1' : '#94a3b8'
          }}>
            {i + 1}
          </button>
        ))}
      </div>

      {/* Question card */}
      <div style={{ background:'#fff', border:'1.5px solid #e2e8f0',
        borderRadius:16, padding:'1.75rem', marginBottom:16,
        boxShadow:'0 2px 8px rgba(0,0,0,0.06)' }}>
        <p style={{ fontSize:17, fontWeight:600, color:'#1e293b',
          lineHeight:1.65, marginBottom:24 }}>
          {q.question}
        </p>
        <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
          {['a','b','c','d'].map(opt => {
            const selected = answers[q.id] === opt
            return (
              <div key={opt} onClick={() => selectAnswer(q.id, opt)}
                style={{
                  padding:'13px 16px', borderRadius:12, cursor:'pointer',
                  border:`2px solid ${selected ? '#6366f1' : '#e2e8f0'}`,
                  background: selected ? '#eef2ff' : '#fafafa',
                  display:'flex', alignItems:'center', gap:12,
                  transition:'all 0.12s'
                }}
                onMouseEnter={e => {
                  if (!selected) {
                    e.currentTarget.style.borderColor = '#a5b4fc'
                    e.currentTarget.style.background = '#f5f3ff'
                  }
                }}
                onMouseLeave={e => {
                  if (!selected) {
                    e.currentTarget.style.borderColor = '#e2e8f0'
                    e.currentTarget.style.background = '#fafafa'
                  }
                }}>
                <div style={{
                  width:28, height:28, borderRadius:8, flexShrink:0,
                  background: selected ? '#6366f1' : '#e2e8f0',
                  color: selected ? '#fff' : '#64748b',
                  display:'flex', alignItems:'center', justifyContent:'center',
                  fontWeight:700, fontSize:12
                }}>
                  {opt.toUpperCase()}
                </div>
                <span style={{ fontSize:14, color: selected ? '#3730a3' : '#374151',
                  fontWeight: selected ? 500 : 400 }}>
                  {q[`option_${opt}`]}
                </span>
              </div>
            )
          })}
        </div>
        <div style={{ marginTop: 24, padding: 16, background: '#f8fafc', borderRadius: 12, border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#475569', marginBottom: 8 }}>📝 Personal Notes (Optional)</div>
          <textarea
            placeholder="Type any formulas or concepts to remember here..."
            value={notes[q.id] || ''}
            onChange={e => setNotes(prev => ({ ...prev, [q.id]: e.target.value }))}
            style={{ width: '100%', height: 60, padding: 10, borderRadius: 8, border: '1px solid #cbd5e1', fontSize: 13, outline: 'none', resize: 'vertical' }}
          />
        </div>
      </div>

      {/* Navigation */}
      <div style={{ display:'flex', gap:10 }}>
        {current > 0 && (
          <button onClick={() => setCurrent(c => c - 1)}
            style={{ padding:'11px 20px', border:'1.5px solid #e2e8f0',
              borderRadius:10, background:'#fff', cursor:'pointer',
              fontSize:14, color:'#475569', fontWeight:500 }}>
            ← Prev
          </button>
        )}
        {current < questions.length - 1 ? (
          <button onClick={() => setCurrent(c => c + 1)}
            style={{ flex:1, padding:'11px',
              background: answers[q.id] ? '#6366f1' : '#e2e8f0',
              color: answers[q.id] ? '#fff' : '#94a3b8',
              border:'none', borderRadius:10,
              fontSize:14, fontWeight:600, cursor: answers[q.id] ? 'pointer' : 'default' }}>
            Next →
          </button>
        ) : (
          <button onClick={submitQuiz}
            disabled={answered < questions.length}
            style={{ flex:1, padding:'11px',
              background: answered >= questions.length ? '#6366f1' : '#e2e8f0',
              color: answered >= questions.length ? '#fff' : '#94a3b8',
              border:'none', borderRadius:10, fontSize:14, fontWeight:600,
              cursor: answered >= questions.length ? 'pointer' : 'default' }}>
            {answered < questions.length
              ? `Answer all questions (${questions.length - answered} left)`
              : 'Submit Quiz ✓'}
          </button>
        )}
      </div>
    </div>
  )

  // ── Result screen ──────────────────────────────────────────
  if (phase === 'result' && result) return (
    <div style={{ maxWidth:560, margin:'0 auto' }}>
      {/* Score card */}
      <div style={{
        background: result.score >= 70 ? 'linear-gradient(135deg,#f0fdf4,#dcfce7)'
          : result.score >= 50 ? 'linear-gradient(135deg,#fffbeb,#fef3c7)'
          : 'linear-gradient(135deg,#fef2f2,#fee2e2)',
        border:`2px solid ${result.score>=70?'#86efac':result.score>=50?'#fcd34d':'#fca5a5'}`,
        borderRadius:20, padding:'2rem', textAlign:'center', marginBottom:20
      }}>
        <div style={{ fontSize:64, fontWeight:800,
          color: result.score>=70?'#16a34a':result.score>=50?'#d97706':'#dc2626' }}>
          {result.score}%
        </div>
        <div style={{ fontSize:16, color:'#475569', marginTop:4 }}>
          {result.correct} / {result.total} correct
        </div>
        <div style={{ fontSize:13, color:'#64748b', marginTop:6 }}>
          {selSubject.name} · {selTopic.name}
        </div>
        {xpEarned > 0 && (
          <div style={{ marginTop:12, display:'inline-flex', alignItems:'center',
            gap:6, background:'rgba(255,255,255,0.7)', padding:'6px 14px',
            borderRadius:99, fontSize:13, fontWeight:600, color:'#6366f1' }}>
            +{xpEarned} XP earned
          </div>
        )}
        <div style={{ fontSize:14, color:'#475569', marginTop:12 }}>
          {result.score >= 70 ? '🎉 Great job! Next review has been scheduled.'
           : result.score >= 50 ? '📚 Not bad. Review this topic soon.'
           : '⚠️ Needs more work. Review scheduled for tomorrow.'}
        </div>

        {/* Confidence rating */}
        <div style={{ marginTop:20 }}>
          <p style={{ fontSize:13, fontWeight:500, color:'#374151', marginBottom:10 }}>
            How confident do you feel?
          </p>
          <div style={{ display:'flex', justifyContent:'center', gap:8 }}>
            {[1,2,3,4,5].map(n => (
              <button key={n} onClick={() => setRating(n)} style={{
                width:38, height:38, borderRadius:10,
                border:`2px solid ${rating===n?'#6366f1':'#e2e8f0'}`,
                background: rating===n?'#6366f1':'rgba(255,255,255,0.8)',
                color: rating===n?'#fff':'#64748b',
                fontWeight:700, cursor:'pointer', fontSize:14
              }}>{n}</button>
            ))}
          </div>
        </div>
      </div>

      {/* Answer breakdown */}
      {Object.keys(result.results || {}).length > 0 && (
        <div style={{ marginBottom:20 }}>
          <h3 style={{ fontSize:14, fontWeight:700, color:'#1e293b', marginBottom:10 }}>
            Answer breakdown
          </h3>
          {questions.map((qq, idx) => {
            const r = result.results[String(qq.id)]
            if (!r) return null
            return (
              <div key={qq.id} style={{
                background: r.correct ? '#f0fdf4' : '#fef2f2',
                border:`1.5px solid ${r.correct?'#86efac':'#fca5a5'}`,
                borderRadius:12, padding:'12px 14px', marginBottom:8
              }}>
                <div style={{ display:'flex', gap:8, alignItems:'flex-start' }}>
                  <div style={{
                    width:22, height:22, borderRadius:6, flexShrink:0,
                    background: r.correct?'#16a34a':'#dc2626',
                    color:'#fff', display:'flex', alignItems:'center',
                    justifyContent:'center', fontSize:12, fontWeight:700
                  }}>
                    {r.correct ? '✓' : '✗'}
                  </div>
                  <div style={{ flex:1 }}>
                    <div style={{ fontSize:13, fontWeight:500, color:'#1e293b',
                      lineHeight:1.5 }}>
                      Q{idx+1}. {qq.question}
                    </div>
                    {!r.correct && (
                      <div style={{ fontSize:12, color:'#64748b', marginTop:4 }}>
                        You chose: <b style={{color:'#dc2626'}}>
                          {r.chosen?.toUpperCase() || '—'}
                        </b>
                        {' · '}Correct: <b style={{color:'#16a34a'}}>
                          {r.answer?.toUpperCase()}
                        </b>
                      </div>
                    )}
                    {r.explanation && (
                      <div style={{ fontSize:11, color:'#64748b',
                        marginTop:4, fontStyle:'italic' }}>
                        {r.explanation}
                      </div>
                    )}
                    {notes[qq.id] && (
                      <div style={{ marginTop: 8, padding: 10, background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 8 }}>
                        <div style={{ fontSize: 11, fontWeight: 600, color: '#d97706', marginBottom: 4 }}>📝 YOUR NOTES:</div>
                        <div style={{ fontSize: 12, color: '#92400e', whiteSpace: 'pre-wrap' }}>{notes[qq.id]}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div style={{ display:'flex', gap:10 }}>
        <button onClick={() => setPhase('topic')}
          style={{ flex:1, padding:'11px', border:'1.5px solid #e2e8f0',
            borderRadius:10, background:'#fff', cursor:'pointer',
            fontSize:14, fontWeight:600, color:'#475569' }}>
          Try another topic
        </button>
        <button onClick={reset}
          style={{ flex:1, padding:'11px', background:'#6366f1',
            color:'#fff', border:'none', borderRadius:10,
            fontSize:14, fontWeight:600, cursor:'pointer' }}>
          New subject
        </button>
      </div>
    </div>
  )

  return null
}

function subjectEmoji(name) {
  const map = {
    'Physics':'⚡', 'Chemistry':'🧪', 'Mathematics':'📐', 'Biology':'🧬',
    'Accountancy':'📊', 'Business Studies':'💼', 'Economics':'📈',
    'History':'🏛️', 'Political Science':'🗳️', 'Geography':'🌍',
    'Psychology':'🧠', 'Data Structures':'🌲', 'Algorithms':'⚙️',
    'DBMS':'🗄️', 'Operating Systems':'💻', 'Computer Networks':'🌐',
    'System Design':'🏗️'
  }
  return map[name] || '📚'
}
