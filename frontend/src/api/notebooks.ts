import api from './index'

export interface Notebook {
  id: number
  name: string
  description?: string
  created_at: string
  updated_at?: string
}

export interface Document {
  id: number
  notebook_id: number
  filename: string
  file_type: string
  file_url: string
  file_size: number
  content?: string
  status: string
  created_at: string
}

export interface Conversation {
  id: number
  notebook_id: number
  title: string
  created_at: string
}

export interface Message {
  id: number | string
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export const notebooksApi = {
  list: () => api.get<Notebook[]>('/notebooks/'),
  
  create: (data: { name: string; description?: string }) => 
    api.post<Notebook>('/notebooks/', data),
  
  get: (id: number) => api.get<Notebook>(`/notebooks/${id}`),
  
  delete: (id: number) => api.delete(`/notebooks/${id}`),
  
  getDocuments: (id: number) => api.get<Document[]>(`/notebooks/${id}/documents`)
}

export const documentsApi = {
  upload: (notebookId: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<Document>(`/documents/upload/${notebookId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  delete: (id: number) => api.delete(`/documents/${id}`)
}

export const chatApi = {
  stream: async (
    data: { notebook_id: number; conversation_id?: number; message: string },
    onChunk: (chunk: { type: string; content?: string; message?: string; conversation_id?: number }) => void
  ) => {
    const response = await fetch('/api/v1/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }))
      onChunk({ type: 'error', message: errorData.detail || `HTTP ${response.status}` })
      return
    }
    
    const reader = response.body?.getReader()
    if (!reader) {
      onChunk({ type: 'error', message: 'No response body' })
      return
    }
    
    const decoder = new TextDecoder()
    let buffer = ''
    
    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          if (buffer.trim()) {
            processBuffer(buffer, onChunk)
          }
          break
        }
        
        const text = decoder.decode(value, { stream: true })
        buffer += text
        
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            processLine(line, onChunk)
          }
        }
      }
    } catch (error) {
      onChunk({ type: 'error', message: error instanceof Error ? error.message : 'Stream error' })
    }
  },
  
  getConversations: (notebookId: number) => 
    api.get<Conversation[]>(`/chat/conversations/${notebookId}`),
  
  getMessages: (conversationId: number) => 
    api.get<Message[]>(`/chat/messages/${conversationId}`),
  
  deleteConversation: (conversationId: number) =>
    api.delete(`/chat/conversations/${conversationId}`)
}

function processBuffer(buffer: string, onChunk: (chunk: any) => void) {
  const lines = buffer.split('\n')
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      processLine(line, onChunk)
    }
  }
}

function processLine(line: string, onChunk: (chunk: any) => void) {
  try {
    const jsonStr = line.slice(6).trim()
    if (jsonStr) {
      const data = JSON.parse(jsonStr)
      onChunk(data)
    }
  } catch (e) {
    // Ignore parse errors for incomplete JSON
  }
}

export const contentApi = {
  generate: (data: { notebook_id: number; content_type: string; custom_prompt?: string }) => 
    api.post('/content/generate', data),
  
  streamGenerate: async (
    data: { notebook_id: number; content_type: string; custom_prompt?: string },
    onChunk: (chunk: { type: string; content?: string; message?: string }) => void
  ) => {
    const response = await fetch('/api/v1/content/stream/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }))
      onChunk({ type: 'error', message: errorData.detail || `HTTP ${response.status}` })
      return
    }
    
    const reader = response.body?.getReader()
    if (!reader) {
      onChunk({ type: 'error', message: 'No response body' })
      return
    }
    
    const decoder = new TextDecoder()
    let buffer = ''
    
    try {
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          if (buffer.trim()) {
            processBuffer(buffer, onChunk)
          }
          break
        }
        
        const text = decoder.decode(value, { stream: true })
        buffer += text
        
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            processLine(line, onChunk)
          }
        }
      }
    } catch (error) {
      onChunk({ type: 'error', message: error instanceof Error ? error.message : 'Stream error' })
    }
  },
  
  getTypes: () => api.get('/content/types')
}

export const podcastApi = {
  generateAudio: async (script: string): Promise<Blob> => {
    const response = await fetch('/api/v1/podcast/convert-script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ script })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    return await response.blob()
  }
}
