/**
 * Formats markdown-style text to HTML
 * Converts:
 * - * bullet points to proper list items
 * - Preserves line breaks
 * - Converts bold **text** to <strong>
 */
export const formatText = (text) => {
  if (!text) return ''
  
  // Split by lines
  const lines = text.split('\n')
  const formatted = []
  let inList = false
  
  lines.forEach((line) => {
    const trimmed = line.trim()
    
    // Check for bullet points (starts with * or -)
    if (trimmed.match(/^[\*\-\•]\s+/)) {
      if (!inList) {
        formatted.push('<ul style="margin: 10px 0; padding-left: 25px;">')
        inList = true
      }
      // Remove the bullet marker and wrap in <li>
      const content = trimmed.replace(/^[\*\-\•]\s+/, '')
      formatted.push(`<li style="margin: 5px 0;">${formatInline(content)}</li>`)
    } else if (trimmed.match(/^\d+\.\s+/)) {
      // Numbered list
      if (!inList) {
        formatted.push('<ol style="margin: 10px 0; padding-left: 25px;">')
        inList = true
      }
      const content = trimmed.replace(/^\d+\.\s+/, '')
      formatted.push(`<li style="margin: 5px 0;">${formatInline(content)}</li>`)
    } else {
      // Regular line
      if (inList) {
        formatted.push('</ul>')
        inList = false
      }
      
      if (trimmed) {
        formatted.push(`<p style="margin: 8px 0;">${formatInline(trimmed)}</p>`)
      } else {
        formatted.push('<br>')
      }
    }
  })
  
  // Close any open list
  if (inList) {
    formatted.push('</ul>')
  }
  
  return formatted.join('')
}

/**
 * Formats inline markdown (bold, italic)
 */
const formatInline = (text) => {
  if (!text) return ''
  
  // Escape HTML first to prevent XSS
  text = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // Convert **bold** to <strong>
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  
  // Note: Single * italic is tricky to parse correctly without lookbehind
  // Skipping italic for now to avoid false matches with bullet points
  
  return text
}
