export default function BacklogAlert({ alert }) {
  const COLORS = {
    critical: { bg: '#fef2f2', border: '#fca5a5',
                text: '#dc2626', badge: '#fee2e2' },
    warning:  { bg: '#fffbeb', border: '#fcd34d',
                text: '#d97706', badge: '#fef3c7' },
    safe:     { bg: '#f0fdf4', border: '#86efac',
                text: '#16a34a', badge: '#dcfce7' },
  }

  const c = COLORS[alert.alert_level] || COLORS.safe

  return (
    <div style={{
      background: c.bg, border: `1px solid ${c.border}`,
      borderRadius: 10, padding: '14px 16px', marginBottom: 10
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between',
        alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 15,
            color: c.text }}>
            {alert.subject_name}
          </div>
          {alert.exam_name && (
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
              {alert.exam_name}
              {alert.exam_date && ` · ${alert.exam_date}`}
            </div>
          )}
        </div>
        <span style={{
          background: c.badge, color: c.text,
          fontSize: 12, fontWeight: 700,
          padding: '4px 10px', borderRadius: 99,
          whiteSpace: 'nowrap'
        }}>
          {alert.severity_label} {alert.severity_10}/10
        </span>
      </div>

      {/* Severity bar */}
      <div style={{ height: 6, background: '#e2e8f0',
        borderRadius: 99, marginBottom: 10, overflow: 'hidden' }}>
        <div style={{
          height: '100%', borderRadius: 99,
          width: `${alert.severity_10 * 10}%`,
          background: c.text,
          transition: 'width 0.6s ease'
        }} />
      </div>

      <p style={{ fontSize: 13, color: '#475569',
        lineHeight: 1.6, marginBottom: 10 }}>
        {alert.message}
      </p>

      {/* Catch-up plan */}
      {alert.catchup_plan && (
        <div style={{ background: 'rgba(255,255,255,0.7)',
          borderRadius: 8, padding: '10px 12px', fontSize: 12 }}>
          <div style={{ fontWeight: 600, color: '#374151',
            marginBottom: 5 }}>
            Catch-up plan
          </div>
          <p style={{ color: '#475569', lineHeight: 1.5,
            marginBottom: 8 }}>
            {alert.catchup_plan.advice}
          </p>
          <div style={{ display: 'flex', gap: 16,
            color: '#64748b', flexWrap: 'wrap' }}>
            <span>
              Chapters left: <strong>
                {alert.catchup_plan.chapters_remaining}
              </strong>
            </span>
            <span>
              Days to exam: <strong>
                {alert.catchup_plan.days_to_exam}
              </strong>
            </span>
            <span>
              Per day: <strong>
                {alert.catchup_plan.chapters_per_day}
              </strong>
            </span>
          </div>
        </div>
      )}
    </div>
  )
}