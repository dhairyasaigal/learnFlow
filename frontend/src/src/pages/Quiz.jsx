import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function Quiz({ user }) {
  const [subjects,   setSubjects]   = useState([])
  const [topics,     setTopics]     = useState([])
  const [questions,  setQuestions]  = useState([])
  const [selSubject, setSelSubject] = useState('')
  const [selTopic,   setSelTopic]   = useState('')
  const [current,    setCurrent]    = useState(0)
  const [answers,    setAnswers]    = useState({})
  const [submitted,  setSubmitted]  = useState(false)
  const [result,     setResult]     = useState(null)
  const [rating,     setRating]     = useState(3)
  const [startTime,  setStartTime]  = useState(null)
  const [loading,    setLoading]    = useState(false)

  useEffect(() => {
    axios.get(`${API}/subjects/${user.user_id}`)
      .then(r => setSubjects(r.data.subjects))
  }, [])

  const loadTopics = async (subjectId) => {
    setSelSubject(subjectId)
    const sub = subjects.find(s => s.id == subjectId)
    if (!sub) return
    const res = await axios.get(
      `${API}/curriculum/${sub.stream}`
    )
    const topicList = res.data.subjects[sub.name] || []
    setTopics(topicList)
  }

  const startQuiz = async () => {
    if (!selTopic) return
    setLoading(true)
    try {
      const res = await axios.get(
        `${API}/quiz/${selTopic}/questions`
      )
      setQuestions(res.data.questions)
      setCurrent(0)
      setAnswers({})
      setSubmitted(false)
      setResult(null)
      setStartTime(Date.now())
    } catch {
      alert('No questions found for this topic yet.')
    } finally { setLoading(false) }
  }

  const selectAnswer = (qId, option) => {
    if (submitted) return
    setAnswers(prev => ({ ...prev, [qId]: option }))
  }

  const submitQuiz = async () => {
    const timeMins = (Date.now() - startTime) / 60000
    const correct  = questions.filter(
      q => answers[q.id] === q.answer
    ).length
    const score    = Math.round((correct / questions.length) * 100)

    setSubmitted(true)
    setResult({ score, correct, total: questions.length })

    try {
      await axios.post(`${API}/quiz/submit/${user.user_id}`, {
        topic_id:    parseInt(selTopic),
        score,
        time_spent:  timeMins,
        self_rating: rating,
        difficulty:  3
      })
    } catch (e) {
      console.error('Submit error:', e)
    }
  }

  const resetQuiz = () => {
    setQuestions([])
    setAnswers({})
    setSubmitted(false)
    setResult(null)
    setSelTopic('')
  }

  const q = questions[current]

  return (
    <div>
      <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>
        Quiz
      </h1>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
        Test your knowledge — AI will schedule your next review
      </p>

      {/* Setup */}
      {questions.length === 0 && (
        <div style={{ background: '#fff', border: '1px solid #e2e8f0',
          borderRadius: 12, padding: '1.5rem', maxWidth: 480 }}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 13, fontWeight: 500,
              display: 'block', marginBottom: 5 }}>Subject</label>
            <select value={selSubject}
              onChange={e => loadTopics(e.target.value)}
              style={{ width: '100%', padding: '10px 12px',
                border: '1px solid #e2e8f0', borderRadius: 8,
                fontSize: 14, background: '#fff' }}>
              <option value=''>Select subject...</option>
              {subjects.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          {topics.length > 0 && (
            <div style={{ marginBottom: 14 }}>
              <label style={{ fontSize: 13, fontWeight: 500,
                display: 'block', marginBottom: 5 }}>Topic</label>
              <select value={selTopic}
                onChange={e => setSelTopic(e.target.value)}
                style={{ width: '100%', padding: '10px 12px',
                  border: '1px solid #e2e8f0', borderRadius: 8,
                  fontSize: 14, background: '#fff' }}>
                <option value=''>Select topic...</option>
                {topics.map(t => (
                  <option key={t.name} value={t.name}>
                    {t.name} (difficulty: {t.difficulty}/5)
                  </option>
                ))}
              </select>
            </div>
          )}

          <button onClick={startQuiz}
            disabled={!selTopic || loading}
            style={{ width: '100%', padding: '11px',
              background: (!selTopic || loading) ? '#c7d2fe' : '#6366f1',
              color: '#fff', border: 'none', borderRadius: 8,
              fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
            {loading ? 'Loading questions...' : 'Start Quiz'}
          </button>
        </div>
      )}

      {/* Quiz in progress */}
      {questions.length > 0 && !submitted && q && (
        <div style={{ maxWidth: 580 }}>
          {/* Progress */}
          <div style={{ display: 'flex', justifyContent: 'space-between',
            alignItems: 'center', marginBottom: 16 }}>
            <span style={{ fontSize: 13, color: '#64748b' }}>
              Question {current + 1} of {questions.length}
            </span>
            <div style={{ display: 'flex', gap: 4 }}>
              {questions.map((_, i) => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: i < current ? '#6366f1'
                            : i === current ? '#6366f1'
                            : '#e2e8f0'
                }} />
              ))}
            </div>
          </div>

          <div style={{ background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 12, padding: '1.5rem', marginBottom: 12 }}>
            <p style={{ fontSize: 16, fontWeight: 500,
              lineHeight: 1.6, marginBottom: 20 }}>
              {q.question}
            </p>
            {['a','b','c','d'].map(opt => (
              <div key={opt}
                onClick={() => selectAnswer(q.id, opt)}
                style={{
                  padding: '10px 14px', borderRadius: 8,
                  marginBottom: 8, cursor: 'pointer',
                  border: `1.5px solid ${answers[q.id] === opt
                    ? '#6366f1' : '#e2e8f0'}`,
                  background: answers[q.id] === opt ? '#eef2ff' : '#fff',
                  fontSize: 14, transition: 'all 0.1s'
                }}>
                <span style={{ fontWeight: 600,
                  color: '#6366f1', marginRight: 8 }}>
                  {opt.toUpperCase()}.
                </span>
                {q[`option_${opt}`]}
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            {current > 0 && (
              <button onClick={() => setCurrent(c => c - 1)}
                style={{ padding: '10px 20px', border: '1px solid #e2e8f0',
                  borderRadius: 8, background: '#fff', cursor: 'pointer',
                  fontSize: 14 }}>
                Back
              </button>
            )}
            {current < questions.length - 1 ? (
              <button onClick={() => setCurrent(c => c + 1)}
                disabled={!answers[q.id]}
                style={{ flex: 1, padding: '10px',
                  background: answers[q.id] ? '#6366f1' : '#c7d2fe',
                  color: '#fff', border: 'none', borderRadius: 8,
                  fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                Next
              </button>
            ) : (
              <button onClick={submitQuiz}
                disabled={Object.keys(answers).length < questions.length}
                style={{ flex: 1, padding: '10px',
                  background: Object.keys(answers).length < questions.length
                    ? '#c7d2fe' : '#6366f1',
                  color: '#fff', border: 'none', borderRadius: 8,
                  fontSize: 14, fontWeight: 600, cursor: 'pointer' }}>
                Submit Quiz
              </button>
            )}
          </div>
        </div>
      )}

      {/* Result */}
      {submitted && result && (
        <div style={{ maxWidth: 480 }}>
          <div style={{ background: '#fff', border: '1px solid #e2e8f0',
            borderRadius: 12, padding: '2rem', textAlign: 'center',
            marginBottom: 16 }}>
            <div style={{ fontSize: 56, fontWeight: 700,
              color: result.score >= 70 ? '#16a34a'
                   : result.score >= 50 ? '#d97706' : '#dc2626' }}>
              {result.score}%
            </div>
            <div style={{ fontSize: 15, color: '#64748b', marginTop: 4 }}>
              {result.correct} / {result.total} correct
            </div>
            <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 8 }}>
              {result.score >= 70 ? 'Great job! Next review scheduled.'
               : result.score >= 50 ? 'Not bad. Review soon.'
               : 'Needs work. Review tomorrow.'}
            </div>

            {/* Self rating */}
            <div style={{ marginTop: 20 }}>
              <p style={{ fontSize: 13, fontWeight: 500,
                marginBottom: 8 }}>
                How confident do you feel about this topic?
              </p>
              <div style={{ display: 'flex',
                justifyContent: 'center', gap: 8 }}>
                {[1,2,3,4,5].map(n => (
                  <button key={n} onClick={() => setRating(n)} style={{
                    width: 36, height: 36, borderRadius: '50%',
                    border: `2px solid ${rating === n ? '#6366f1' : '#e2e8f0'}`,
                    background: rating === n ? '#6366f1' : '#fff',
                    color: rating === n ? '#fff' : '#64748b',
                    fontWeight: 600, cursor: 'pointer', fontSize: 13
                  }}>{n}</button>
                ))}
              </div>
            </div>
          </div>

          <button onClick={resetQuiz} style={{
            width: '100%', padding: '11px',
            background: '#6366f1', color: '#fff',
            border: 'none', borderRadius: 8,
            fontSize: 14, fontWeight: 600, cursor: 'pointer'
          }}>
            Take Another Quiz
          </button>
        </div>
      )}
    </div>
  )
}