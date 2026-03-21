import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'

export default function Landing() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div style={{ fontFamily: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif', color: '#1e293b' }}>

      {/* Navbar */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: scrolled ? 'rgba(255,255,255,0.95)' : 'transparent',
        backdropFilter: scrolled ? 'blur(10px)' : 'none',
        borderBottom: scrolled ? '1px solid #e2e8f0' : 'none',
        padding: '0 2rem', height: 64,
        display: 'flex', alignItems: 'center',
        justifyContent: 'space-between',
        transition: 'all 0.3s ease'
      }}>
        <div style={{ fontWeight: 800, fontSize: 22, color: '#6366f1' }}>
          LearnFlow
        </div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <Link to='/login' style={{
            padding: '8px 18px', borderRadius: 8,
            fontSize: 14, fontWeight: 500,
            color: '#6366f1', textDecoration: 'none',
            border: '1.5px solid #6366f1',
            transition: 'all 0.2s'
          }}>
            Login
          </Link>
          <Link to='/register' style={{
            padding: '8px 18px', borderRadius: 8,
            fontSize: 14, fontWeight: 600,
            background: '#6366f1', color: '#fff',
            textDecoration: 'none',
            transition: 'all 0.2s'
          }}>
            Get started free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section style={{
        minHeight: '100vh', display: 'flex',
        flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', textAlign: 'center',
        padding: '6rem 2rem 4rem',
        background: 'linear-gradient(135deg, #f0f4ff 0%, #faf5ff 50%, #f0fdf4 100%)'
      }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: '#eef2ff', color: '#6366f1',
          padding: '6px 16px', borderRadius: 99,
          fontSize: 13, fontWeight: 600, marginBottom: 28,
          border: '1px solid #c7d2fe'
        }}>
          Built for Indian students · LSTM-powered AI
        </div>

        <h1 style={{
          fontSize: 'clamp(36px, 6vw, 72px)',
          fontWeight: 800, lineHeight: 1.1,
          marginBottom: 24, maxWidth: 800
        }}>
          Stop forgetting what{' '}
          <span style={{ color: '#6366f1' }}>you already know</span>
        </h1>

        <p style={{
          fontSize: 18, color: '#64748b', lineHeight: 1.7,
          maxWidth: 560, marginBottom: 40
        }}>
          LearnFlow uses two LSTM neural networks to learn your personal
          forgetting curve and predict backlog crises before they happen —
          so you study smarter, not harder.
        </p>

        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap',
          justifyContent: 'center' }}>
          <Link to='/register' style={{
            padding: '14px 32px', borderRadius: 10,
            fontSize: 16, fontWeight: 700,
            background: '#6366f1', color: '#fff',
            textDecoration: 'none',
            boxShadow: '0 4px 20px rgba(99,102,241,0.35)'
          }}>
            Start for free
          </Link>
          <a href='#how-it-works' style={{
            padding: '14px 32px', borderRadius: 10,
            fontSize: 16, fontWeight: 600,
            background: '#fff', color: '#6366f1',
            textDecoration: 'none',
            border: '1.5px solid #c7d2fe'
          }}>
            How it works
          </a>
        </div>

        {/* Stats row */}
        <div style={{
          display: 'flex', gap: 48, marginTop: 64,
          flexWrap: 'wrap', justifyContent: 'center'
        }}>
          {[
            { num: '2',       label: 'LSTM models'              },
            { num: '50k+',    label: 'Training sequences'       },
            { num: '7',       label: 'Indian exam streams'      },
            { num: '99.9%',   label: 'AUC on forgetting model'  },
          ].map(s => (
            <div key={s.label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 800,
                color: '#6366f1' }}>{s.num}</div>
              <div style={{ fontSize: 13, color: '#94a3b8',
                marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Problem section */}
      <section style={{
        padding: '6rem 2rem', background: '#fff',
        textAlign: 'center'
      }}>
        <p style={{ fontSize: 13, fontWeight: 700, color: '#6366f1',
          letterSpacing: '0.1em', textTransform: 'uppercase',
          marginBottom: 12 }}>The problem</p>
        <h2 style={{ fontSize: 36, fontWeight: 800,
          marginBottom: 16, maxWidth: 600, margin: '0 auto 16px' }}>
          99% of students are not toppers
        </h2>
        <p style={{ fontSize: 16, color: '#64748b', maxWidth: 560,
          margin: '0 auto 4rem', lineHeight: 1.7 }}>
          You understand a concept today. You forget it in a week.
          You don't realise you have a backlog until 3 days before the exam.
          Sound familiar?
        </p>

        <div style={{ display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 24, maxWidth: 900, margin: '0 auto' }}>
          {[
            {
              emoji: '🧠',
              title: 'Memory decay',
              desc: 'You forget 70% of what you learn within 24 hours if you don\'t review it at the right time.'
            },
            {
              emoji: '📚',
              title: 'Silent backlog',
              desc: 'Topics pile up quietly. By the time you notice, you have 8 chapters left and 5 days to exam.'
            },
            {
              emoji: '🎯',
              title: 'Wrong priorities',
              desc: 'Students waste time re-reading chapters they already know instead of fixing actual gaps.'
            }
          ].map(p => (
            <div key={p.title} style={{
              background: '#f8fafc', borderRadius: 16,
              padding: '2rem', textAlign: 'left',
              border: '1px solid #e2e8f0'
            }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>{p.emoji}</div>
              <h3 style={{ fontSize: 17, fontWeight: 700,
                marginBottom: 8 }}>{p.title}</h3>
              <p style={{ fontSize: 14, color: '#64748b',
                lineHeight: 1.6 }}>{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id='how-it-works' style={{
        padding: '6rem 2rem',
        background: 'linear-gradient(135deg, #f0f4ff, #faf5ff)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <p style={{ fontSize: 13, fontWeight: 700, color: '#6366f1',
            letterSpacing: '0.1em', textTransform: 'uppercase',
            marginBottom: 12 }}>How it works</p>
          <h2 style={{ fontSize: 36, fontWeight: 800 }}>
            Two AI models working together
          </h2>
        </div>

        <div style={{ display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 24, maxWidth: 900, margin: '0 auto 4rem' }}>

          {/* Model A */}
          <div style={{
            background: '#fff', borderRadius: 20,
            padding: '2rem', border: '2px solid #c7d2fe'
          }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: '#eef2ff', color: '#6366f1',
              padding: '4px 12px', borderRadius: 99,
              fontSize: 12, fontWeight: 700, marginBottom: 16
            }}>
              Model A
            </div>
            <h3 style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
              Forgetting curve LSTM
            </h3>
            <p style={{ fontSize: 14, color: '#64748b',
              lineHeight: 1.7, marginBottom: 20 }}>
              Learns your personal memory decay rate per topic.
              Reads your last 10 quiz sessions and predicts
              exactly when you'll forget — then schedules a review
              one day before that happens.
            </p>
            <div style={{ background: '#f8fafc', borderRadius: 12,
              padding: '1rem', fontSize: 13 }}>
              <div style={{ fontWeight: 600, marginBottom: 8,
                color: '#374151' }}>Input features per session:</div>
              {[
                'Quiz score (0–100)',
                'Time spent studying',
                'Days since last review',
                'Topic difficulty (from JEE/NEET syllabus)',
                'Self-confidence rating (1–5)'
              ].map(f => (
                <div key={f} style={{ display: 'flex', gap: 8,
                  marginBottom: 4, color: '#64748b' }}>
                  <span style={{ color: '#6366f1' }}>→</span> {f}
                </div>
              ))}
            </div>
            <div style={{ marginTop: 16, display: 'flex',
              gap: 16, fontSize: 13 }}>
              <div>
                <div style={{ fontWeight: 700, color: '#6366f1',
                  fontSize: 18 }}>76.6%</div>
                <div style={{ color: '#94a3b8' }}>Accuracy</div>
              </div>
              <div>
                <div style={{ fontWeight: 700, color: '#6366f1',
                  fontSize: 18 }}>0.999</div>
                <div style={{ color: '#94a3b8' }}>AUC-ROC</div>
              </div>
              <div>
                <div style={{ fontWeight: 700, color: '#6366f1',
                  fontSize: 18 }}>50k</div>
                <div style={{ color: '#94a3b8' }}>Training samples</div>
              </div>
            </div>
          </div>

          {/* Model B */}
          <div style={{
            background: '#fff', borderRadius: 20,
            padding: '2rem', border: '2px solid #bbf7d0'
          }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: '#f0fdf4', color: '#16a34a',
              padding: '4px 12px', borderRadius: 99,
              fontSize: 12, fontWeight: 700, marginBottom: 16
            }}>
              Model B
            </div>
            <h3 style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
              Backlog predictor LSTM
            </h3>
            <p style={{ fontSize: 14, color: '#64748b',
              lineHeight: 1.7, marginBottom: 20 }}>
              Watches 14 days of your study behaviour per subject
              and predicts backlog severity 2 weeks before your exam.
              Fires an alert and generates a day-by-day catch-up plan.
            </p>
            <div style={{ background: '#f8fafc', borderRadius: 12,
              padding: '1rem', fontSize: 13 }}>
              <div style={{ fontWeight: 600, marginBottom: 8,
                color: '#374151' }}>Input features per day:</div>
              {[
                'Topics covered today',
                'Study time in minutes',
                'Quiz score',
                'Days skipped streak',
                'Chapters remaining',
                'Days to exam'
              ].map(f => (
                <div key={f} style={{ display: 'flex', gap: 8,
                  marginBottom: 4, color: '#64748b' }}>
                  <span style={{ color: '#16a34a' }}>→</span> {f}
                </div>
              ))}
            </div>
            <div style={{ marginTop: 16, display: 'flex',
              gap: 16, fontSize: 13 }}>
              <div>
                <div style={{ fontWeight: 700, color: '#16a34a',
                  fontSize: 18 }}>0.60</div>
                <div style={{ color: '#94a3b8' }}>MAE (0–10 scale)</div>
              </div>
              <div>
                <div style={{ fontWeight: 700, color: '#16a34a',
                  fontSize: 18 }}>0.005</div>
                <div style={{ color: '#94a3b8' }}>MSE loss</div>
              </div>
              <div>
                <div style={{ fontWeight: 700, color: '#16a34a',
                  fontSize: 18 }}>54k</div>
                <div style={{ color: '#94a3b8' }}>Training samples</div>
              </div>
            </div>
          </div>
        </div>

        {/* Flow diagram */}
        <div style={{ maxWidth: 700, margin: '0 auto',
          background: '#fff', borderRadius: 20,
          padding: '2rem', border: '1px solid #e2e8f0' }}>
          <h3 style={{ fontSize: 16, fontWeight: 700,
            textAlign: 'center', marginBottom: 24 }}>
            How data flows through LearnFlow
          </h3>
          <div style={{ display: 'flex', alignItems: 'center',
            justifyContent: 'center', gap: 0, flexWrap: 'wrap' }}>
            {[
              { label: 'Take quiz',       color: '#eef2ff', text: '#6366f1' },
              { label: '→', color: 'transparent', text: '#94a3b8', arrow: true },
              { label: 'Log study',       color: '#f0fdf4', text: '#16a34a' },
              { label: '→', color: 'transparent', text: '#94a3b8', arrow: true },
              { label: 'LSTM A + B run',  color: '#fef3c7', text: '#d97706' },
              { label: '→', color: 'transparent', text: '#94a3b8', arrow: true },
              { label: 'Smart dashboard', color: '#fce7f3', text: '#db2777' },
            ].map((s, i) => (
              <div key={i} style={{
                background: s.color,
                padding: s.arrow ? '0 4px' : '8px 16px',
                borderRadius: 8, fontSize: s.arrow ? 18 : 13,
                fontWeight: s.arrow ? 400 : 600,
                color: s.text
              }}>
                {s.label}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '6rem 2rem', background: '#fff' }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <p style={{ fontSize: 13, fontWeight: 700, color: '#6366f1',
            letterSpacing: '0.1em', textTransform: 'uppercase',
            marginBottom: 12 }}>Features</p>
          <h2 style={{ fontSize: 36, fontWeight: 800 }}>
            Everything the 99% needs
          </h2>
        </div>

        <div style={{ display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 20, maxWidth: 960, margin: '0 auto' }}>
          {[
            {
              icon: '📅',
              title: 'Personalised review schedule',
              desc: 'Not generic intervals — the LSTM learns your specific forgetting rate per topic and schedules reviews at exactly the right moment.'
            },
            {
              icon: '🚨',
              title: 'Backlog early warning',
              desc: 'Get alerted 2 weeks before backlog becomes a crisis. Includes a chapter-by-chapter catch-up plan.'
            },
            {
              icon: '🎯',
              title: 'Adaptive quizzes',
              desc: 'Questions adapt to your performance. Hard topics get harder questions. Weak topics get revision questions.'
            },
            {
              icon: '📊',
              title: 'Study log tracker',
              desc: 'Log offline study sessions manually. The AI incorporates them into your backlog prediction.'
            },
            {
              icon: '🇮🇳',
              title: 'Built for Indian curriculum',
              desc: 'Covers PCM (JEE), PCB (NEET), Commerce, Arts, and University streams with NCERT chapter mappings.'
            },
            {
              icon: '🔥',
              title: 'Streaks + XP system',
              desc: 'Daily streaks and XP rewards keep you coming back. Study habits built through consistency.'
            },
          ].map(f => (
            <div key={f.title} style={{
              background: '#f8fafc', borderRadius: 16,
              padding: '1.5rem', border: '1px solid #e2e8f0'
            }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>{f.icon}</div>
              <h3 style={{ fontSize: 15, fontWeight: 700,
                marginBottom: 8 }}>{f.title}</h3>
              <p style={{ fontSize: 13, color: '#64748b',
                lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Indian student types */}
      <section style={{
        padding: '6rem 2rem',
        background: 'linear-gradient(135deg, #f0f4ff, #faf5ff)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <p style={{ fontSize: 13, fontWeight: 700, color: '#6366f1',
            letterSpacing: '0.1em', textTransform: 'uppercase',
            marginBottom: 12 }}>Who is this for</p>
          <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 12 }}>
            Trained on real Indian student patterns
          </h2>
          <p style={{ fontSize: 16, color: '#64748b', maxWidth: 500,
            margin: '0 auto' }}>
            Our AI was trained on 5 student archetypes
            identified from Indian study behaviour research
          </p>
        </div>

        <div style={{ display: 'flex', gap: 12, maxWidth: 960,
          margin: '0 auto', flexWrap: 'wrap', justifyContent: 'center' }}>
          {[
            { label: 'Last-minute crammer', pct: '35%',
              color: '#fef2f2', text: '#dc2626',
              desc: 'Does nothing until 2 weeks before exam' },
            { label: 'Chapter skipper',     pct: '20%',
              color: '#fffbeb', text: '#d97706',
              desc: 'Skips hard chapters, does easy ones only' },
            { label: 'Coaching dependent',  pct: '15%',
              color: '#f0fdf4', text: '#16a34a',
              desc: 'Only studies on coaching class days' },
            { label: 'Burnout student',     pct: '15%',
              color: '#faf5ff', text: '#7c3aed',
              desc: 'Starts strong, collapses mid-semester' },
            { label: 'Consistent studier',  pct: '15%',
              color: '#eef2ff', text: '#6366f1',
              desc: 'The target — LearnFlow helps you get here' },
          ].map(t => (
            <div key={t.label} style={{
              background: t.color, border: `1.5px solid ${t.text}22`,
              borderRadius: 14, padding: '1.25rem',
              minWidth: 160, flex: '1'
            }}>
              <div style={{ fontWeight: 800, fontSize: 22,
                color: t.text, marginBottom: 4 }}>{t.pct}</div>
              <div style={{ fontWeight: 600, fontSize: 13,
                color: t.text, marginBottom: 6 }}>{t.label}</div>
              <div style={{ fontSize: 12, color: '#64748b',
                lineHeight: 1.5 }}>{t.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{
        padding: '6rem 2rem', background: '#6366f1',
        textAlign: 'center'
      }}>
        <h2 style={{ fontSize: 40, fontWeight: 800,
          color: '#fff', marginBottom: 16 }}>
          Start studying smarter today
        </h2>
        <p style={{ fontSize: 18, color: '#c7d2fe',
          marginBottom: 40, maxWidth: 480, margin: '0 auto 40px' }}>
          Free forever. No credit card. Built for JEE, NEET,
          boards and university placements.
        </p>
        <Link to='/register' style={{
          padding: '16px 40px', borderRadius: 12,
          fontSize: 17, fontWeight: 700,
          background: '#fff', color: '#6366f1',
          textDecoration: 'none',
          boxShadow: '0 4px 24px rgba(0,0,0,0.15)'
        }}>
          Create free account
        </Link>
      </section>

      {/* Footer */}
      <footer style={{
        padding: '2rem', background: '#1e293b',
        textAlign: 'center', color: '#64748b', fontSize: 13
      }}>
        LearnFlow · Built with LSTM neural networks ·
        For Indian students · {new Date().getFullYear()}
      </footer>

    </div>
  )
}