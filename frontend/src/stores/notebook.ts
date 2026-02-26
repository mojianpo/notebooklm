import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Notebook, Document, Conversation, Message } from '../api/notebooks'
import { notebooksApi, chatApi } from '../api/notebooks'

export const useNotebookStore = defineStore('notebook', () => {
  const currentNotebook = ref<Notebook | null>(null)
  const documents = ref<Document[]>([])
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const messages = ref<Message[]>([])

  const loadNotebook = async (id: number) => {
    currentNotebook.value = await notebooksApi.get(id)
    documents.value = await notebooksApi.getDocuments(id)
    conversations.value = await chatApi.getConversations(id)
  }

  const loadMessages = async (conversationId: number) => {
    messages.value = await chatApi.getMessages(conversationId)
  }

  const selectConversation = async (conversation: Conversation) => {
    currentConversation.value = conversation
    await loadMessages(conversation.id)
  }

  const setCurrentConversationId = (id: number | null) => {
    if (id) {
      currentConversation.value = {
        id: id,
        notebook_id: currentNotebook.value?.id || 0,
        title: '',
        created_at: new Date().toISOString()
      }
    } else {
      currentConversation.value = null
    }
  }

  const addMessage = (message: Message) => {
    const exists = messages.value.find(m => m.id === message.id)
    if (!exists) {
      messages.value.push(message)
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  const reset = () => {
    currentNotebook.value = null
    documents.value = []
    conversations.value = []
    currentConversation.value = null
    messages.value = []
  }

  return {
    currentNotebook,
    documents,
    conversations,
    currentConversation,
    messages,
    loadNotebook,
    loadMessages,
    selectConversation,
    setCurrentConversationId,
    addMessage,
    clearMessages,
    reset
  }
})
