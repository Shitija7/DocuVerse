import { useState, useEffect } from 'react'
import { summarizeDocument, getUserDocuments } from '../api'
import { formatText } from '../utils/formatter'
import './Summarize.css'

function Summarize({ token, userId }) {
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(false)
  const [documents, setDocuments] = useState([])
  const [selectedDocId, setSelectedDocId] = useState('')
  const [loadingDocs, setLoadingDocs] = useState(true)

  useEffect(() => {
    if (userId && token) {
      loadDocuments()
    }
  }, [userId, token])

  const loadDocuments = async () => {
    try {
      const result = await getUserDocuments(userId, token)
      setDocuments(result.documents || [])
      if (result.documents && result.documents.length > 0) {
        setSelectedDocId(result.documents[0].id)
      }
    } catch (err) {
      console.error('Failed to load documents:', err)
    } finally {
      setLoadingDocs(false)
    }
  }

  const handleSummarize = async () => {
    if (!selectedDocId) {
      setSummary('Please select a document to summarize')
      return
    }

    setLoading(true)
    setSummary('')
    
    try {
      const result = await summarizeDocument(userId, selectedDocId, token)
      setSummary(result.summary || 'No summary available')
    } catch (err) {
      setSummary('❌ Error: ' + (err.response?.data?.summary || 'Failed to generate summary'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="summarize">
      <h2>Document Summarizer</h2>
      <p className="description">
        Generate AI-powered summaries of your uploaded documents
      </p>
      
      <div className="summarize-content">
        {loadingDocs ? (
          <div className="loading-docs">Loading documents...</div>
        ) : documents.length === 0 ? (
          <div className="no-docs">No documents uploaded yet. Upload a document first.</div>
        ) : (
          <>
            <div className="document-selector">
              <label htmlFor="doc-select">Select Document:</label>
              <select 
                id="doc-select"
                value={selectedDocId} 
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="doc-select"
              >
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))}
              </select>
            </div>
            
            <button onClick={handleSummarize} disabled={loading} className="summarize-btn">
              {loading ? 'Generating Summary...' : '🔍 Generate Summary'}
            </button>
          </>
        )}
        
        {summary && (
          <div 
            className="summary-result"
            dangerouslySetInnerHTML={{ __html: formatText(summary) }}
          />
        )}
      </div>
    </div>
  )
}

export default Summarize

