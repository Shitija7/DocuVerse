import { useState, useRef, useEffect } from 'react'
import { askQuestion } from '../api'
import { formatText } from '../utils/formatter'
import './Chat.css'

function Chat({ token, userId }) {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Hello! I can answer questions about your uploaded documents. What would you like to know?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await askQuestion(userMessage, userId, token)
      
      // Add bot response
      setMessages(prev => [...prev, { role: 'bot', content: response.answer }])
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: '❌ Error: ' + (err.response?.data?.detail || 'Failed to get response') 
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat">
      <h2>Chat with Your Documents</h2>
      
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.role === 'bot' && <span className="message-icon">🤖</span>}
              {msg.role === 'user' && <span className="message-icon">👤</span>}
              {msg.role === 'bot' ? (
                <div 
                  className="message-text"
                  dangerouslySetInnerHTML={{ __html: formatText(msg.content) }}
                />
              ) : (
                <div className="message-text">{msg.content}</div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="message-content">
              <span className="message-icon">🤖</span>
              <div className="message-text loading">Thinking...</div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={loading}
          autoFocus
        />
        <button type="submit" disabled={!input.trim() || loading}>
          Send
        </button>
      </form>
    </div>
  )
}

export default Chat

