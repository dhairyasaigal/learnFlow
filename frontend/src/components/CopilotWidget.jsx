import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function CopilotWidget({ user }) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([
    { role: 'model', text: 'Hi! I am your AI Copilot. How can I help you study today?' }
  ])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, open])

  const checkCopilot = async () => {
    if (!query.trim() || loading) return
    const currentQ = query
    setQuery('')
    const newHistory = [...messages, { role: 'user', text: currentQ }]
    setMessages(newHistory)
    setLoading(true)

    try {
      const res = await axios.post(`${API}/copilot/chat/${user.user_id}`, {
        message: currentQ,
        history: messages.slice(1) // omit the hardcoded intro
      })
      setMessages(msg => [...msg, { role: 'model', text: res.data.reply }])
    } catch (e) {
      setMessages(msg => [...msg, { role: 'model', text: 'Sorry, I hit a snag connecting to my brain. Try again?' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 9999 }}>
      {open ? (
        <div style={{
          width: 350, height: 500, background: '#fff', borderRadius: 16,
          boxShadow: '0 10px 25px rgba(0,0,0,0.1)', display: 'flex', flexDirection: 'column',
          border: '1px solid #e2e8f0', overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #6366f1, #4f46e5)', color: '#fff',
            padding: '14px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <div style={{ fontWeight: 600, fontSize: 16 }}>✨ AI Study Copilot</div>
            <button onClick={() => setOpen(false)} style={{
              background: 'transparent', border: 'none', color: '#fff', fontSize: 20, cursor: 'pointer'
            }}>×</button>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: 16, background: '#f8fafc', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.map((m, i) => (
              <div key={i} style={{
                alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                background: m.role === 'user' ? '#6366f1' : '#fff',
                color: m.role === 'user' ? '#fff' : '#1e293b',
                padding: '10px 14px', borderRadius: 12, maxWidth: '85%', fontSize: 14,
                boxShadow: m.role==='model'?'0 1px 3px rgba(0,0,0,0.05)':'none',
                border: m.role==='model'?'1px solid #e2e8f0':'none',
                lineHeight: 1.5,
                whiteSpace: 'pre-wrap'
              }}>
                {m.text}
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: 'flex-start', fontSize: 13, color: '#64748b' }}>Thinking...</div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div style={{ padding: 12, background: '#fff', borderTop: '1px solid #e2e8f0', display: 'flex', gap: 8 }}>
            <input
              value={query} onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && checkCopilot()}
              placeholder="Ask me a doubt..."
              style={{
                flex: 1, padding: '10px 14px', borderRadius: 99, border: '1px solid #cbd5e1', outline: 'none', fontSize: 14
              }}
            />
            <button onClick={checkCopilot} disabled={loading || !query.trim()} style={{
              background: '#6366f1', color: '#fff', border: 'none', borderRadius: 99, width: 40, height: 40, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: (!query.trim() || loading) ? 0.6 : 1
            }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
        </div>
      ) : (
        <button onClick={() => setOpen(true)} style={{
          width: 56, height: 56, borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
          color: '#fff', border: 'none', boxShadow: '0 4px 14px rgba(99,102,241,0.4)', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, transition: 'transform 0.2s'
        }} onMouseEnter={e => e.currentTarget.style.transform='scale(1.05)'} onMouseLeave={e => e.currentTarget.style.transform='scale(1)'}>
          ✨
        </button>
      )}
    </div>
  )
}
