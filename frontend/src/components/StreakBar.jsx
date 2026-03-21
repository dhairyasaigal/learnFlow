export default function StreakBar({ streak, xp }) {
  const days    = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const today   = new Date().getDay()
  const adjusted = today === 0 ? 6 : today - 1

  return (
    <div style={{
      background: '#fff', border: '1px solid #e2e8f0',
      borderRadius: 12, padding: '1rem 1.25rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 12 }}>
        <div style={{ fontSize: 14, fontWeight: 600,
          color: '#1e293b' }}>
          Weekly streak
        </div>
        <div style={{ display: 'flex', alignItems: 'center',
          gap: 6 }}>
          <span style={{ fontSize: 18 }}>🔥</span>
          <span style={{ fontWeight: 700, fontSize: 16,
            color: '#ea580c' }}>
            {streak} day{streak !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Day bubbles */}
      <div style={{ display: 'flex', gap: 6,
        justifyContent: 'space-between' }}>
        {days.map((day, i) => {
          const isActive  = i <= adjusted && streak > (adjusted - i)
          const isToday   = i === adjusted
          return (
            <div key={day} style={{ textAlign: 'center', flex: 1 }}>
              <div style={{
                width: '100%', aspectRatio: '1',
                borderRadius: '50%', marginBottom: 4,
                background: isActive ? '#6366f1'
                          : isToday  ? '#eef2ff' : '#f1f5f9',
                border: isToday
                  ? '2px solid #6366f1' : '2px solid transparent',
                display: 'flex', alignItems: 'center',
                justifyContent: 'center',
                fontSize: 12,
                color: isActive ? '#fff' : '#94a3b8'
              }}>
                {isActive ? '✓' : ''}
              </div>
              <div style={{ fontSize: 10, color: '#94a3b8' }}>
                {day}
              </div>
            </div>
          )
        })}
      </div>

      {/* XP bar */}
      <div style={{ marginTop: 14 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between',
          fontSize: 12, color: '#64748b', marginBottom: 5 }}>
          <span>XP progress</span>
          <span style={{ fontWeight: 600, color: '#ca8a04' }}>
            ⚡ {xp} XP
          </span>
        </div>
        <div style={{ height: 6, background: '#f1f5f9',
          borderRadius: 99, overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 99,
            width: `${Math.min((xp % 500) / 5, 100)}%`,
            background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
            transition: 'width 0.6s ease'
          }} />
        </div>
        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
          {500 - (xp % 500)} XP to next level
        </div>
      </div>
    </div>
  )
}