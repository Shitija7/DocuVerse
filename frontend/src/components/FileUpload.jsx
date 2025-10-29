import { useState } from 'react'
import { uploadFile } from '../api'
import './FileUpload.css'

function FileUpload({ token, userId }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setMessage('')
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) {
      setMessage('Please select a file')
      setIsError(true)
      return
    }

    setUploading(true)
    setMessage('')

    try {
      const result = await uploadFile(file, userId, token)
      setMessage(`✅ File "${result.filename}" uploaded successfully! (${result.text_length} chars)`)
      setIsError(false)
      setFile(null)
      // Reset file input
      document.getElementById('file-input').value = ''
    } catch (err) {
      setMessage(err.response?.data?.error || 'Upload failed')
      setIsError(true)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="file-upload">
      <h2>Upload Document</h2>
      <p className="description">Upload PDF or TXT files to build your knowledge base</p>
      
      <form onSubmit={handleUpload} className="upload-form">
        <div className="file-input-wrapper">
          <input
            id="file-input"
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileChange}
            disabled={uploading}
          />
          {file && <div className="file-name">📄 {file.name}</div>}
        </div>
        
        <button type="submit" disabled={!file || uploading}>
          {uploading ? 'Uploading...' : 'Upload File'}
        </button>
      </form>

      {message && (
        <div className={`upload-message ${isError ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    </div>
  )
}

export default FileUpload

