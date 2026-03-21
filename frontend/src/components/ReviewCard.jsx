export default function ReviewCard({ item }) {
  const URGENCY = {
    today: { bg: '#fef2f2', border: '#fca5a5',
              text: '#dc2626', label: 'Due today' },
    soon:  { bg: '#fffbeb', border: '#fcd34d',
              text: '#d97706', label: 'Due soon'  },
    later: { bg: '#f0fdf4', border: '#86efac',
              text: '#16a34a', label: 'On track'  },
  }

  const u = URGENCY[item.urgency] || URGENCY.later

  return (
    <div style={{
      background: u.bg, border: `1px solid ${u.border}`,
      borderRadius: 10, padding: '12px 14px', marginBottom: 8
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between',
        alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <div style={{ fontWeight: 500, fontSize: 14,
            color: '#1e293b' }}>
            {item.topic_name}
          </div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
            {item.subject_name}
          </div>
        </div>
        <span style={{
          background: '#fff', color: u.text,
          border: `1px solid ${u.border}`,
          fontSize: 11, fontWeight: 600,
          padding: '3px 8px', borderRadius: 99,
          whiteSpace: 'nowrap'
        }}>
          {u.label}
        </span>
      </div>

      <p style={{ fontSize: 12, color: '#64748b',
        lineHeight: 1.5, marginBottom: 8 }}>
        {item.message}
      </p>

      {/* Recall probability bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between',
          fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>
          <span>Recall probability</span>
          <span>{Math.round(item.recall_prob * 100)}%</span>
        </div>
        <div style={{ height: 4, background: '#e2e8f0',
          borderRadius: 99, overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 99,
            width: `${Math.round(item.recall_prob * 100)}%`,
            background: item.recall_prob > 0.6 ? '#16a34a'
                      : item.recall_prob > 0.4 ? '#d97706'
                      : '#dc2626',
            transition: 'width 0.6s ease'
          }} />
        </div>
      </div>
    </div>
  )
}