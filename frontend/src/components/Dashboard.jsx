import { useState, useEffect } from 'react'
import './Dashboard.css'
import FileUpload from './FileUpload'
import Chat from './Chat'
import Summarize from './Summarize'

function Dashboard({ token, userId, onLogout }) {
  const [activeTab, setActiveTab] = useState('upload')
  const username = localStorage.getItem('username') || 'User'
  
  const [chatMessages, setChatMessages] = useState(() => {
    const saved = localStorage.getItem('chatMessages')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch (e) {
        return [
          { role: 'system', content: 'Hello! I can answer questions about your uploaded documents. What would you like to know?' }
        ]
      }
    }
    return [
      { role: 'system', content: 'Hello! I can answer questions about your uploaded documents. What would you like to know?' }
    ]
  })
  
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(chatMessages))
  }, [chatMessages])

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>📚 DocuVerse</h1>
        <div className="header-actions">
          <span className="username">{username}</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="tabs">
          <button 
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            📁 Upload Documents
          </button>
          <button 
            className={activeTab === 'chat' ? 'active' : ''}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
          <button 
            className={activeTab === 'summarize' ? 'active' : ''}
            onClick={() => setActiveTab('summarize')}
          >
            📝 Summarize
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'upload' && <FileUpload token={token} userId={userId} />}
          {activeTab === 'chat' && (
            <Chat 
              token={token} 
              userId={userId} 
              messages={chatMessages}
              setMessages={setChatMessages}
            />
          )}
          {activeTab === 'summarize' && <Summarize token={token} userId={userId} />}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

