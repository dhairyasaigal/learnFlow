import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts'

const API = 'http://localhost:8000'

export default function Analytics({ user }) {
  const [data, setData] = useState(null)
  
  useEffect(() => {
    axios.get(`${API}/analytics/${user.user_id}`).then(r => setData(r.data))
  }, [user.user_id])

  if (!data) return <div style={{padding: 40, textAlign: 'center'}}>Loading ML Analytics...</div>

  return (
    <div style={{ paddingBottom: 60 }}>
      {/* Header */}
      <div style={{ marginBottom: 30 }}>
         <h1 style={{ fontSize: 24, fontWeight: 700 }}>ML Inference & Analytics 🧪</h1>
         <p style={{ color: '#64748b' }}>Advanced forgetting curves and exam predictions based on your study history.</p>
      </div>

      {/* Predictions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 30 }}>
         <div style={{ background: '#f8fafc', padding: 20, borderRadius: 12, border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: 13, color: '#64748b', fontWeight: 600 }}>PREDICTED EXAM SCORE</div>
            <div style={{ fontSize: 32, fontWeight: 800, color: '#10b981', marginTop: 10 }}>{data.predicted_score}%</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 5 }}>Based on average accuracy & recent progress</div>
         </div>
         <div style={{ background: '#f8fafc', padding: 20, borderRadius: 12, border: '1px solid #e2e8f0' }}>
            <div style={{ fontSize: 13, color: '#64748b', fontWeight: 600 }}>PREDICTED COMPETITIVE RANK (EST.)</div>
            <div style={{ fontSize: 32, fontWeight: 800, color: '#6366f1', marginTop: 10 }}>#{data.predicted_rank.toLocaleString()}</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 5 }}>In a standard population of 50k candidates</div>
         </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Retention Curves */}
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 15 }}>Decay / Forgetting Curves (Ebbinghaus)</h2>
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, marginBottom: 30 }}>
            {data.retention_curves.map(curve => (
              <div key={curve.topic} style={{ marginBottom: 30 }}>
                <h3 style={{ fontSize: 14, fontWeight: 500, color: '#475569', marginBottom: 10 }}>{curve.topic}</h3>
                <div style={{ width: '100%', height: 200 }}>
                  <ResponsiveContainer>
                    <LineChart data={curve.curve} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="day" style={{ fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={v => `Day ${v}`} />
                      <YAxis domain={[0, 100]} style={{ fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={v => `${v}%`} />
                      <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                      <Line type="monotone" dataKey="recall" name="Recall Probability" stroke="#f43f5e" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ))}
            {data.retention_curves.length === 0 && (
              <div style={{ padding: 20, textAlign: 'center', color: '#94a3b8', fontSize: 14 }}>Not enough data to model retention curves yet. Start studying topics!</div>
            )}
          </div>
        </div>

        {/* Heatmap/Bar Chart */}
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 15 }}>Subject Proficiency Heatmap</h2>
          <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 20, height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.heatmap} margin={{ top: 5, right: 0, left: -20, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="subject" style={{ fontSize: 11 }} tickLine={false} axisLine={false} angle={-35} textAnchor="end" interval={0} />
                  <YAxis domain={[0, 100]} style={{ fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={v => `${v}%`} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="score" name="Average Proficiency" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
