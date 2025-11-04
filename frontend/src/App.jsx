import { useState, useEffect } from 'react'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [token, setToken] = useState(null)
  const [currentUserId, setCurrentUserId] = useState(null)

  useEffect(() => {
    // Check for stored token
    const storedToken = localStorage.getItem('token')
    const storedUserId = localStorage.getItem('userId')
    if (storedToken) {
      setToken(storedToken)
      setCurrentUserId(storedUserId)
      setIsAuthenticated(true)
    }
  }, [])

  const handleLogin = (authToken, userId, username) => {
    setToken(authToken)
    setCurrentUserId(userId)
    setIsAuthenticated(true)
    localStorage.setItem('token', authToken)
    localStorage.setItem('userId', userId)
    localStorage.setItem('username', username)
  }

  const handleLogout = () => {
    setToken(null)
    setCurrentUserId(null)
    setIsAuthenticated(false)
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    localStorage.removeItem('chatMessages')
  }

  return (
    <div className="App">
      {!isAuthenticated ? (
        <Login onLogin={handleLogin} />
      ) : (
        <Dashboard token={token} userId={currentUserId} onLogout={handleLogout} />
      )}
    </div>
  )
}

export default App

