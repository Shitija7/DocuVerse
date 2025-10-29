import { useState } from 'react'
import './Dashboard.css'
import FileUpload from './FileUpload'
import Chat from './Chat'
import Summarize from './Summarize'

function Dashboard({ token, userId, onLogout }) {
  const [activeTab, setActiveTab] = useState('upload')
  const username = localStorage.getItem('username') || 'User'

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
          {activeTab === 'chat' && <Chat token={token} userId={userId} />}
          {activeTab === 'summarize' && <Summarize token={token} userId={userId} />}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

