import { Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Dashboard from './pages/Dashboard.jsx'
import Quiz      from './pages/Quiz.jsx'
import StudyLog  from './pages/StudyLog.jsx'
import Subjects  from './pages/Subjects.jsx'
import StudyPlan from './pages/StudyPlan.jsx'
import Login     from './pages/login.jsx'
import Register  from './pages/register.jsx'
import Landing   from './pages/landing.jsx'
import Analytics from './pages/Analytics.jsx'
import Navbar    from './components/navbar.jsx'

export default function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('learnflow_user')
    return saved ? JSON.parse(saved) : null
  })

  const login = (userData) => {
    localStorage.setItem('learnflow_user', JSON.stringify(userData))
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('learnflow_user')
    setUser(null)
  }

  if (!user) {
    return (
      <Routes>
        <Route path='/'         element={<Landing />} />
        <Route path='/login'    element={<Login    onLogin={login} />} />
        <Route path='/register' element={<Register onLogin={login} />} />
        <Route path='*'         element={<Navigate to='/' />} />
      </Routes>
    )
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      <Navbar user={user} onLogout={logout} />
      <div style={{ maxWidth: 960, margin: '0 auto',
        padding: '1.5rem 1rem' }}>
        <Routes>
          <Route path='/'         element={<Dashboard user={user} />} />
          <Route path='/quiz'     element={<Quiz       user={user} />} />
          <Route path='/log'      element={<StudyLog   user={user} />} />
          <Route path='/subjects' element={<Subjects   user={user} />} />
          <Route path='/plan'     element={<StudyPlan  user={user} />} />
          <Route path='/analytics' element={<Analytics user={user} />} />
          <Route path='*'         element={<Navigate to='/' />} />
        </Routes>
      </div>
    </div>
  )
}