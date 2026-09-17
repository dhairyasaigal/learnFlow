import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

// Lightweight markdown renderer — bold, italic, bullets, code, headers
function renderMarkdown(text) {
  if (!text) return ''
  const lines = text.split('\n')
  const output = []
  let inCode   = false
  let codeBuffer = []

  const escHtml = s => s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  const inlineFormat = s =>
    escHtml(s)
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g,     '<em>$1</em>')
      .replace(/`(.+?)`/g,       '<code style="background:#f1f5f9;padding:1px 4px;border-radius:4px;font-size:12px">$1</code>')

  for (const line of lines) {
    if (line.startsWith('```')) {
      if (inCode) {
        output.push(`<pre style="background:#1e293b;color:#f8fafc;padding:10px;border-radius:8px;font-size:12px;overflow-x:auto;margin:6px 0">${codeBuffer.join('\n')}</pre>`)
        codeBuffer = []
        inCode = false
      } else {
        inCode = true
      }
      continue
    }
    if (inCode) { codeBuffer.push(escHtml(line)); continue }

    if (/^#{1,3}\s/.test(line)) {
      const level = line.match(/^(#{1,3})/)[0].length
      const content = inlineFormat(line.replace(/^#{1,3}\s/, ''))
      output.push(`<h${level+1} style="margin:8px 0 4px;font-size:${level===1?15:14}px">${content}</h${level+1}>`)
    } else if (/^[\-\*]\s/.test(line)) {
      output.push(`<li style="margin:2px 0;margin-left:12px">${inlineFormat(line.replace(/^[\-\*]\s/, ''))}</li>`)
    } else if (line.trim() === '') {
      output.push('<br/>')
    } else {
      output.push(`<span>${inlineFormat(line)}</span><br/>`)
    }
  }
  return output.join('')
}

// Quick-action prompts for the student
const QUICK_ACTIONS = [
  { label: '📊 My weak topics',     prompt: 'What are my weakest topics and how should I study them?' },
  { label: '📅 Study plan',          prompt: 'Based on my progress, what should I study today?' },
  { label: '❌ Explain my mistakes', prompt: 'Can you explain the questions I got wrong recently?' },
  { label: '🔁 Review schedule',     prompt: 'Which topics should I review today to improve retention?' },
]

export default function CopilotWidget({ user }) {
  const [open,           setOpen]           = useState(false)
  const [query,          setQuery]          = useState('')
  const [messages,       setMessages]       = useState([
    { role: 'model', text: '✨ Hi! I\'m your AI Study Copilot. I can see your quiz history, weak topics, and study data.\n\nAsk me anything, or try one of the quick actions below!' }
  ])
  const [loading,        setLoading]        = useState(false)
  const [conversationId, setConversationId] = useState('')
  const [showActions,    setShowActions]    = useState(true)
  const messagesEndRef  = useRef(null)
  const inputRef        = useRef(null)

  const scrollToBottom = () =>
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })

  useEffect(() => { scrollToBottom() }, [messages, open])

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [open])

  const sendMessage = async (text) => {
    const msg = (text || query).trim()
    if (!msg || loading) return

    setQuery('')
    setShowActions(false)
    setMessages(prev => [...prev, { role: 'user', text: msg }])
    setLoading(true)

    try {
      const res = await axios.post(`${API}/copilot/chat/${user.user_id}`, {
        message:         msg,
        conversation_id: conversationId,
        history:         messages.slice(1).map(m => ({
          role:    m.role === 'user' ? 'user' : 'assistant',
          content: m.text
        }))
      })
      if (res.data.conversation_id && !conversationId) {
        setConversationId(res.data.conversation_id)
      }
      setMessages(prev => [...prev, { role: 'model', text: res.data.reply }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'model',
        text: '⚠️ Could not reach the AI Copilot. Check that the backend is running.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const startNew = () => {
    setMessages([{
      role: 'model',
      text: '✨ New conversation started! What would you like to explore?'
    }])
    setConversationId('')
    setShowActions(true)
    setQuery('')
  }

  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999 }}>
      {open ? (
        <div style={{
          width: 380, height: 560,
          background: '#fff', borderRadius: 20,
          boxShadow: '0 20px 60px rgba(0,0,0,0.15)',
          display: 'flex', flexDirection: 'column',
          border: '1px solid #e2e8f0', overflow: 'hidden',
          animation: 'fadeInUp 0.2s ease'
        }}>
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
            color: '#fff', padding: '14px 16px',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            flexShrink: 0
          }}>
            <div>
              <div style={{ fontWeight: 700, fontSize: 15 }}>✨ AI Study Copilot</div>
              <div style={{ fontSize: 11, opacity: 0.8 }}>
                Personalized to your study data
              </div>
            </div>
            <div style={{ display: 'flex', gap: 6 }}>
              <button
                onClick={startNew}
                title="New conversation"
                style={{
                  background: 'rgba(255,255,255,0.15)', border: 'none',
                  color: '#fff', fontSize: 13, cursor: 'pointer',
                  borderRadius: 8, padding: '4px 8px'
                }}>
                +
              </button>
              <button
                onClick={() => setOpen(false)}
                style={{
                  background: 'rgba(255,255,255,0.15)', border: 'none',
                  color: '#fff', fontSize: 17, cursor: 'pointer',
                  borderRadius: 8, padding: '4px 8px'
                }}>
                ×
              </button>
            </div>
          </div>

          {/* Messages */}
          <div style={{
            flex: 1, overflowY: 'auto', padding: '12px 14px',
            background: '#f8fafc', display: 'flex',
            flexDirection: 'column', gap: 10
          }}>
            {messages.map((m, i) => (
              <div key={i} style={{
                alignSelf:  m.role === 'user' ? 'flex-end' : 'flex-start',
                background: m.role === 'user' ? '#6366f1' : '#fff',
                color:      m.role === 'user' ? '#fff'    : '#1e293b',
                padding:    '10px 13px', borderRadius: 14,
                maxWidth:   '90%', fontSize: 13,
                boxShadow:  m.role === 'model' ? '0 1px 4px rgba(0,0,0,0.06)' : 'none',
                border:     m.role === 'model' ? '1px solid #e2e8f0' : 'none',
                lineHeight: 1.55
              }}>
                {m.role === 'model' ? (
                  <div dangerouslySetInnerHTML={{ __html: renderMarkdown(m.text) }} />
                ) : (
                  <span>{m.text}</span>
                )}
              </div>
            ))}

            {/* Quick action buttons — shown at start of conversation */}
            {showActions && messages.length <= 1 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 4 }}>
                {QUICK_ACTIONS.map((a, i) => (
                  <button key={i} onClick={() => sendMessage(a.prompt)} style={{
                    background: '#fff', border: '1px solid #e2e8f0',
                    borderRadius: 10, padding: '8px 12px', cursor: 'pointer',
                    textAlign: 'left', fontSize: 13, color: '#374151',
                    transition: 'border-color 0.15s, background 0.15s',
                    fontWeight: 500
                  }}
                    onMouseEnter={e => {
                      e.currentTarget.style.borderColor = '#6366f1'
                      e.currentTarget.style.background  = '#f5f3ff'
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.borderColor = '#e2e8f0'
                      e.currentTarget.style.background  = '#fff'
                    }}
                  >
                    {a.label}
                  </button>
                ))}
              </div>
            )}

            {loading && (
              <div style={{
                alignSelf: 'flex-start', fontSize: 13, color: '#64748b',
                display: 'flex', gap: 4, alignItems: 'center'
              }}>
                <div style={{ display: 'flex', gap: 3 }}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{
                      width: 6, height: 6, borderRadius: '50%',
                      background: '#6366f1', opacity: 0.7,
                      animation: `bounce 1s ${i * 0.2}s infinite`
                    }} />
                  ))}
                </div>
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div style={{
            padding: '10px 12px', background: '#fff',
            borderTop: '1px solid #e2e8f0', display: 'flex', gap: 8,
            flexShrink: 0
          }}>
            <input
              ref={inputRef}
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Ask me a doubt..."
              style={{
                flex: 1, padding: '9px 14px', borderRadius: 99,
                border: '1.5px solid #e2e8f0', outline: 'none',
                fontSize: 13, transition: 'border-color 0.15s'
              }}
              onFocus={e  => e.target.style.borderColor = '#6366f1'}
              onBlur={e   => e.target.style.borderColor = '#e2e8f0'}
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !query.trim()}
              style={{
                background:     '#6366f1', color: '#fff', border: 'none',
                borderRadius:   99, width: 38, height: 38, cursor: 'pointer',
                display:        'flex', alignItems: 'center', justifyContent: 'center',
                opacity:        (!query.trim() || loading) ? 0.5 : 1,
                transition:     'opacity 0.15s',
                flexShrink:     0
              }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2.5"
                strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>

          <style>{`
            @keyframes bounce {
              0%, 60%, 100% { transform: translateY(0) }
              30%            { transform: translateY(-5px) }
            }
            @keyframes fadeInUp {
              from { opacity: 0; transform: translateY(16px) }
              to   { opacity: 1; transform: translateY(0) }
            }
          `}</style>
        </div>
      ) : (
        <button
          onClick={() => setOpen(true)}
          style={{
            width: 58, height: 58, borderRadius: '50%',
            background: 'linear-gradient(135deg, #6366f1, #4f46e5)',
            color: '#fff', border: 'none',
            boxShadow: '0 6px 20px rgba(99,102,241,0.45)',
            cursor: 'pointer', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: 26,
            transition: 'transform 0.2s, box-shadow 0.2s'
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform  = 'scale(1.08)'
            e.currentTarget.style.boxShadow  = '0 8px 28px rgba(99,102,241,0.55)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform  = 'scale(1)'
            e.currentTarget.style.boxShadow  = '0 6px 20px rgba(99,102,241,0.45)'
          }}
          title="AI Study Copilot"
        >
          ✨
        </button>
      )}
    </div>
  )
}
