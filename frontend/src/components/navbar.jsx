import { Link, useLocation } from 'react-router-dom'

export default function Navbar({ user, onLogout }) {
  const loc = useLocation()

  const links = [
    { to: '/',         label: 'Dashboard' },
    { to: '/quiz',     label: 'Quiz'      },
    { to: '/log',      label: 'Study Log' },
    { to: '/subjects', label: 'Subjects'  },
  ]

  return (
    <nav style={{
      background: '#fff', borderBottom: '1px solid #e2e8f0',
      padding: '0 1.5rem', display: 'flex',
      alignItems: 'center', justifyContent: 'space-between',
      height: 56, position: 'sticky', top: 0, zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 28 }}>
        <span style={{ fontWeight: 800, fontSize: 18, color: '#6366f1' }}>
          LearnFlow
        </span>
        <div style={{ display: 'flex', gap: 2 }}>
          {links.map(l => (
            <Link key={l.to} to={l.to} style={{
              padding: '6px 14px', borderRadius: 8,
              fontSize: 14, textDecoration: 'none',
              background: loc.pathname === l.to ? '#eef2ff' : 'transparent',
              color:      loc.pathname === l.to ? '#6366f1' : '#64748b',
              fontWeight: loc.pathname === l.to ? 600 : 400,
              transition: 'all 0.15s'
            }}>
              {l.label}
            </Link>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <StreakPill streak={user.streak} />
        <XpPill xp={user.xp} />
        <span style={{ fontSize: 13, fontWeight: 500,
          color: '#374151' }}>
          {user.name}
        </span>
        <button onClick={onLogout} style={{
          fontSize: 13, padding: '5px 12px',
          border: '1px solid #e2e8f0', borderRadius: 6,
          background: '#fff', cursor: 'pointer',
          color: '#64748b', transition: 'all 0.15s'
        }}>
          Logout
        </button>
      </div>
    </nav>
  )
}

function StreakPill({ streak }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 5,
      background: streak > 0 ? '#fff7ed' : '#f8fafc',
      border: `1px solid ${streak > 0 ? '#fed7aa' : '#e2e8f0'}`,
      borderRadius: 99, padding: '4px 10px', fontSize: 13
    }}>
      <span style={{ fontSize: 14 }}>🔥</span>
      <span style={{ fontWeight: 600,
        color: streak > 0 ? '#ea580c' : '#94a3b8' }}>
        {streak} day{streak !== 1 ? 's' : ''}
      </span>
    </div>
  )
}

function XpPill({ xp }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 5,
      background: '#fefce8', border: '1px solid #fde68a',
      borderRadius: 99, padding: '4px 10px', fontSize: 13
    }}>
      <span style={{ fontSize: 14 }}>⚡</span>
      <span style={{ fontWeight: 600, color: '#ca8a04' }}>
        {xp} XP
      </span>
    </div>
  )
}