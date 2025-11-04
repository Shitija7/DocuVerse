import { useState } from 'react'
import { signup, login } from '../api'
import './Login.css'

function Login({ onLogin }) {
  const [isSignup, setIsSignup] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isSignup) {
        await signup(username, password)
      }
      
      const response = await login(username, password)
      onLogin(response.access_token, response.user_id, response.username)
    } catch (err) {
      console.error(' Authentication error:', err)
      console.error('Error response:', err.response?.data)
      setError(err.response?.data?.detail || err.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>📚 DocuVerse</h1>
        <p className="subtitle">RAG Chatbot Platform</p>
        
        <div className="tab-switch">
          <button 
            className={!isSignup ? 'active' : ''}
            onClick={() => setIsSignup(false)}
          >
            Login
          </button>
          <button 
            className={isSignup ? 'active' : ''}
            onClick={() => setIsSignup(true)}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={loading}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />
          {error && <div className="error-message">{error}</div>}
          <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : (isSignup ? 'Sign Up' : 'Login')}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login

