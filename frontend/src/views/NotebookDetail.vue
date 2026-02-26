<template>
  <div class="notebook-detail" v-loading="loading">
 
    <div class="detail-content">
      <div class="sidebar">
        <div class="sidebar-card glass-card notebook-info-card">
          <div class="notebook-info">
            <button class="back-btn" @click="goBack">
              <el-icon><ArrowLeft /></el-icon>
              <span>返回</span>
            </button>
            <div class="notebook-title-container">
              <h2 class="notebook-title">{{ notebook?.name }}</h2>
            </div>
          </div>
        </div>
        <div class="sidebar-card glass-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Folder /></el-icon>
              <span>文档列表</span>
              <el-tag type="info" size="small" effect="plain">{{ documents.length }}/3</el-tag>
            </div>
            <button 
              class="action-btn small primary" 
              :class="{ disabled: documents.length >= 3 }"
              :disabled="documents.length >= 3"
              @click="documents.length < 3 && (showUploadDialog = true)"
              :title="documents.length >= 3 ? '已达到文档数量上限' : '上传文档'"
            >
              <el-icon><Upload /></el-icon>
              <span>上传</span>
            </button>
          </div>
          
          <div class="document-list">
            <transition-group name="slide">
              <div
                v-for="doc in documents"
                :key="doc.id"
                class="document-item"
              >
                <div class="doc-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="doc-info">
                  <div class="doc-name">{{ doc.filename }}<span class="doc-status" :class="doc.status">
                     【 {{ getStatusText(doc.status) }}】
                    </span></div>
                </div>
                <el-button
                  type="text"
                  size="small"
                  :icon="Delete"
                  class="doc-delete"
                  @click.stop="deleteDocument(doc.id)"
                />
              </div>
            </transition-group>
            
            <el-empty
              v-if="documents.length === 0"
              description="暂无文档"
              :image-size="50"
            />
          </div>
        </div>

        <div class="sidebar-card glass-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><MagicStick /></el-icon>
              <span>AI 工具箱</span>
            </div>
          </div>
          
          <div class="ai-tools-grid">
            <button
              v-for="tool in aiTools"
              :key="tool.id"
              class="ai-tool-btn"
              @click="generateContent(tool.id, tool.name)"
              :class="{ disabled: documents.length === 0 }"
            >
              <div class="tool-icon" :style="{ background: tool.gradient }">
                <el-icon><component :is="tool.icon" /></el-icon>
              </div>
              <span class="tool-name">{{ tool.name }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="main-area">
        <div class="chat-container glass-card">
          <div class="chat-header">
            <div class="chat-title">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI 对话</span>
            </div>
            <div class="chat-actions" v-if="messages.length > 0">
              <el-button type="text" size="small" @click="clearChat">
                <el-icon><Delete /></el-icon>
                清空对话
              </el-button>
            </div>
          </div>
          
          <div class="chat-messages" ref="chatContainer">
            <transition-group name="fade">
              <div
                v-for="msg in messages"
                :key="msg.id"
                :class="['message-wrapper', msg.role]"
              >
                <div class="message-avatar">
                  <div class="avatar-icon" :class="msg.role">
                    <el-icon v-if="msg.role === 'user'"><User /></el-icon>
                    <el-icon v-else><Service /></el-icon>
                  </div>
                </div>
                
                <div class="message-content">
                  <div class="message-header">
                    <span class="message-role">{{ msg.role === 'user' ? '你' : 'AI 助手' }}</span>
                    <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                  </div>
                  <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
                </div>
              </div>
            </transition-group>
            
            <div v-if="isTyping && streamingContent" class="message-wrapper assistant streaming">
              <div class="message-avatar">
                <div class="avatar-icon assistant">
                  <el-icon><Service /></el-icon>
                </div>
              </div>
              
              <div class="message-content">
                <div class="message-header">
                  <span class="message-role">AI 助手</span>
                  <span class="streaming-indicator">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                  </span>
                </div>
                <div class="message-text" v-html="renderMarkdown(streamingContent)"></div>
              </div>
            </div>

            <div v-if="messages.length === 0 && !isTyping" class="welcome-message">
              <div class="welcome-icon">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <h3>开始与 AI 助手对话</h3>
              <p>上传文档后，向 AI 助手提问，获取智能回答</p>
              
              <div class="suggestion-cards">
                <div class="suggestion-card" @click="setInput('总结这篇文档的主要观点')">
                  <el-icon><Document /></el-icon>
                  <span>总结文档要点</span>
                </div>
                <div class="suggestion-card" @click="setInput('文档中提到的关键概念有哪些？')">
                  <el-icon><Key /></el-icon>
                  <span>提取关键概念</span>
                </div>
                <div class="suggestion-card" @click="setInput('请详细解释文档的核心内容')">
                  <el-icon><Reading /></el-icon>
                  <span>深入解读</span>
                </div>
                <div class="suggestion-card" @click="setInput('基于文档内容，有什么建议？')">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>获取建议</span>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input-wrapper">
            <div class="input-container">
              <div class="input-box">
                <textarea
                  v-model="inputMessage"
                  class="chat-textarea"
                  rows="2"
                  maxlength="2000"
                  placeholder="输入您的问题... (Ctrl + Enter 发送)"
                  :disabled="isTyping"
                  @keydown.enter.ctrl="sendMessage"
                ></textarea>
                <button
                  class="send-btn-inline"
                  @click="sendMessage"
                  :disabled="!inputMessage.trim() || isTyping"
                  title="发送消息"
                >
                  <el-icon><Promotion /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="500px"
      class="upload-dialog"
    >
      <div class="upload-area">
        <div v-if="documents.length >= 3" class="upload-limit-warning">
          <el-icon><WarningFilled /></el-icon>
          <span>该笔记本已达到文档数量上限（最多3个），请删除现有文档后再上传。</span>
        </div>
        <template v-else>
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            class="upload-component"
          >
            <div class="upload-icon">
              <el-icon><UploadFilled /></el-icon>
            </div>
            <div class="upload-text">
              <p class="primary-text">拖拽文件到此处或 <em>点击上传</em></p>
              <p class="hint-text">支持 PDF、DOCX、TXT、Markdown、HTML</p>
              <p class="limit-text">当前文档：{{ documents.length }}/3</p>
            </div>
          </el-upload>
          
          <div v-if="selectedFile" class="file-preview">
            <div class="file-info">
              <el-icon><Document /></el-icon>
              <span>{{ selectedFile.name }}</span>
              <el-tag size="small">{{ formatFileSize(selectedFile.size) }}</el-tag>
            </div>
          </div>
        </template>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showUploadDialog = false" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="uploadFile"
            :loading="uploading"
            :disabled="!selectedFile || documents.length >= 3"
            size="large"
          >
            <el-icon><Check /></el-icon>
            开始上传
          </el-button>
        </div>
      </template>
    </el-dialog>

    <div v-if="generatedContent" class="content-result-section glass-card">
      <div class="result-header">
        <h3>生成结果</h3>
        <div class="result-actions">
          <el-button type="text" @click="copyContent">
            <el-icon><DocumentCopy /></el-icon>
            复制
          </el-button>
          <el-button type="text" @click="clearGeneratedContent">
            <el-icon><Delete /></el-icon>
            关闭
          </el-button>
        </div>
      </div>
      <div class="result-body">
        <Mindmap v-if="currentContentType === 'mindmap'" :markdown="generatedContent" />
        <div v-else class="result-content" v-html="renderMarkdown(generatedContent)"></div>
      </div>
    </div>
    
    <div v-else-if="isGenerating" class="generating-section glass-card">
      <div class="generating-animation">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <p>正在生成内容，请稍候...</p>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Upload,
  Document,
  Promotion,
  UploadFilled,
  Notebook,
  Reading,
  ChatLineSquare,
  Picture,
  Files,
  DataAnalysis,
  Microphone,
  VideoPlay,
  Folder,
  MagicStick,
  User,
  Service,
  Delete,
  Key,
  DocumentCopy,
  Check,
  ChatDotRound,
  WarningFilled
} from '@element-plus/icons-vue'
import { useNotebookStore } from '../stores/notebook'
import { documentsApi, chatApi, contentApi } from '../api/notebooks'
import Mindmap from '../components/Mindmap.vue'

const route = useRoute()
const router = useRouter()
const store = useNotebookStore()

const loading = ref(false)
const isTyping = ref(false)
const uploading = ref(false)
const isGenerating = ref(false)

const showUploadDialog = ref(false)
const showContentDialog = ref(false)
const selectedFile = ref<File | null>(null)
const streamingContent = ref('')
const inputMessage = ref('')

const currentContentTool = ref('')
const currentContentType = ref('')
const customPrompt = ref('')
const generatedContent = ref('')

const chatContainer = ref<HTMLElement>()

const notebook = computed(() => store.currentNotebook)
const documents = computed(() => store.documents)
const messages = computed(() => store.messages)

const aiTools = [
  { id: 'report', name: '总结报告', icon: Document, gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { id: 'mindmap', name: '思维导图', icon: Picture, gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { id: 'flashcards', name: '闪卡', icon: Files, gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
  { id: 'quiz', name: '测验', icon: Reading, gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' },
  { id: 'podcast', name: '语音播客', icon: Microphone, gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { id: 'presentation', name: '演示文稿', icon: VideoPlay, gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }
]

const loadNotebook = async () => {
  loading.value = true
  try {
    await store.loadNotebook(Number(route.params.id))
  } catch (error) {
    ElMessage.error('加载笔记本失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/')
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  uploading.value = true
  try {
    await documentsApi.upload(Number(route.params.id), selectedFile.value)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    selectedFile.value = null
    await loadNotebook()
  } catch (error) {
    ElMessage.error('上传失败')
    console.error(error)
  } finally {
    uploading.value = false
  }
}

const deleteDocument = async (docId: any) => {
  const numericId = Number(docId)
  if (!docId ) {
    ElMessage.error('文档ID无效：' + docId)
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '确认删除', {
      type: 'warning'
    })
    await documentsApi.delete(numericId)
    ElMessage.success('删除成功')
    await loadNotebook()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isTyping.value) return
  
  const userMessage = inputMessage.value
  inputMessage.value = ''
  
  isTyping.value = true
  streamingContent.value = ''
  
  const tempUserMsg = {
    id: `temp-${Date.now()}`,
    conversation_id: store.currentConversation?.id || 0,
    role: 'user' as const,
    content: userMessage,
    created_at: new Date().toISOString()
  }
  store.addMessage(tempUserMsg)
  scrollToBottom()
  
  try {
    let conversationId = store.currentConversation?.id
    
    await chatApi.stream(
      {
        notebook_id: Number(route.params.id),
        conversation_id: conversationId,
        message: userMessage
      },
      (chunk) => {
        if (chunk.type === 'content') {
          streamingContent.value += chunk.content
          scrollToBottom()
        } else if (chunk.type === 'done') {
          const assistantMsg = {
            id: `msg-${Date.now()}`,
            conversation_id: chunk.conversation_id,
            role: 'assistant' as const,
            content: streamingContent.value,
            created_at: new Date().toISOString()
          }
          store.addMessage(assistantMsg)
          
          if (!conversationId && chunk.conversation_id) {
            store.setCurrentConversationId(chunk.conversation_id)
          }
          
          streamingContent.value = ''
        } else if (chunk.type === 'error') {
          ElMessage.error(chunk.message)
          streamingContent.value = ''
        }
      }
    )
  } catch (error) {
    ElMessage.error('发送消息失败')
    console.error(error)
    streamingContent.value = ''
  } finally {
    isTyping.value = false
  }
}

const clearChat = async () => {
  try {
    await ElMessageBox.confirm('确定要清空对话记录吗？', '确认清空', {
      type: 'warning'
    })
    store.clearMessages()
    store.setCurrentConversationId(null)
    ElMessage.success('对话已清空')
  } catch (error) {
    // 用户取消
  }
}

const setInput = (text: string) => {
  inputMessage.value = text
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const generateContent = async (type: string, name: string) => {
  if (documents.value.length === 0) {
    ElMessage.warning('请先上传文档')
    return
  }
  
  currentContentType.value = type
  currentContentTool.value = name
  generatedContent.value = ''
  
  ElMessageBox.prompt(
    `请输入${name}的生成提示词（可选）`,
    `生成${name}`,
    {
      confirmButtonText: '生成',
      cancelButtonText: '取消',
      inputPlaceholder: '例如：输入您的额外要求...',
      inputType: 'textarea',
      inputRows: 3,
      showClose: true
    }
  ).then(({ value }) => {
    isGenerating.value = true
    try {
      if (currentContentType.value === 'mindmap') {
        contentApi.generate({
          notebook_id: Number(route.params.id),
          content_type: currentContentType.value,
          custom_prompt: value
        }).then((response: any) => {
          generatedContent.value = response.content
          ElMessage.success('脑图生成成功')
        }).catch((error: any) => {
          ElMessage.error('生成失败: ' + (error.response?.data?.detail || '未知错误'))
          console.error(error)
        }).finally(() => {
          isGenerating.value = false
        })
      } else {
        contentApi.streamGenerate({
          notebook_id: Number(route.params.id),
          content_type: currentContentType.value,
          custom_prompt: value
        }, (chunk) => {
          if (chunk.type === 'content') {
            generatedContent.value += chunk.content
          } else if (chunk.type === 'error') {
            ElMessage.error(chunk.message)
          }
        }).finally(() => {
          isGenerating.value = false
        })
      }
    } catch (error) {
      ElMessage.error('生成失败')
      console.error(error)
      isGenerating.value = false
    }
  }).catch(() => {
    // 取消生成
  })
}

const copyContent = () => {
  let processedContent = generatedContent.value
    .replace(/(#{1,4} )/g, '\n$1')
    .replace(/(\s*\* )/g, '\n$1')
    .replace(/(\s*\d+\. )/g, '\n$1')
    .replace(/(```)/g, '\n$1')
  
  navigator.clipboard.writeText(processedContent)
  ElMessage.success('已复制到剪贴板')
}

const clearGeneratedContent = () => {
  generatedContent.value = ''
}

const renderMarkdown = (text: string) => {
  if (!text) return ''
  
  let html = text
  
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const langLabel = lang ? `<span class="code-lang">${lang}</span>` : ''
    return `<div class="code-block"><div class="code-header">${langLabel}<button class="copy-code-btn" onclick="navigator.clipboard.writeText(\`${code.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">复制</button></div><pre class="markdown-pre"><code>${escapeHtml(code)}</code></pre></div>`
  })
  
  html = html.replace(/`([^`]+)`/g, '<code class="markdown-inline-code">$1</code>')
  
  html = html.replace(/^#### (.+)$/gm, '<h4 class="markdown-h4">$1</h4>')
  html = html.replace(/^### (.+)$/gm, '<h3 class="markdown-h3">$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2 class="markdown-h2">$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1 class="markdown-h1">$1</h1>')
  
  html = html.replace(/^\s*[-*]\s+(.+)$/gm, '<li class="markdown-li">$1</li>')
  html = html.replace(/^\s*\d+\.\s+(.+)$/gm, '<li class="markdown-li markdown-li-ordered">$1</li>')
  
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em class="markdown-bold-italic">$1</em></strong>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="markdown-bold">$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em class="markdown-italic">$1</em>')
  
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="markdown-link" target="_blank" rel="noopener">$1</a>')
  
  html = html.replace(/(<li class="markdown-li[^"]*">.*?<\/li>\n?)+/g, (match) => {
    return `<ul class="markdown-list">${match}</ul>`
  })
  
  html = html.replace(/\n{2,}/g, '</p><p class="markdown-paragraph">')
  html = `<p class="markdown-paragraph">${html}</p>`
  html = html.replace(/<p class="markdown-paragraph"><\/p>/g, '')
  html = html.replace(/<p class="markdown-paragraph">(<h[1-4])/g, '$1')
  html = html.replace(/(<\/h[1-4]>)<\/p>/g, '$1')
  html = html.replace(/<p class="markdown-paragraph">(<ul)/g, '$1')
  html = html.replace(/(<\/ul>)<\/p>/g, '$1')
  html = html.replace(/<p class="markdown-paragraph">(<div class="code-block")/g, '$1')
  html = html.replace(/(<\/div>)<\/p>/g, '$1')
  
  return html
}

const escapeHtml = (text: string) => {
  const htmlEntities: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }
  return text.replace(/[&<>"']/g, char => htmlEntities[char])
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  loadNotebook()
})
</script>
<style scoped>
.notebook-detail {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.08);
  border: none;
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.back-btn:hover {
  background: rgba(102, 126, 234, 0.15);
  transform: translateX(-2px);
}

.notebook-info-card {
  margin-bottom: 20px;
  padding: 16px;
}

.notebook-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notebook-title-container {
  flex: 1;
  min-width: 0;
}

.notebook-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-secondary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.small {
  padding: 6px 12px;
  font-size: 12px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.action-btn.primary:disabled,
.action-btn.primary.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.detail-content {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.sidebar {
  display: flex;
  flex-direction: column;
  min-width: 360px;
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

.sidebar-card {
  padding: 20px;
  display: flex;
  margin-bottom: 10px;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-title .el-icon {
  color: var(--primary-color);
}

.card-title .el-tag {
  margin-left: 8px;
}

.document-list {
  flex: 1;
  overflow-y: auto;
  height: 260px;
  min-height: 260px;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(102, 126, 234, 0.03);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 8px;
}

.document-item:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.15);
  transform: translateX(4px);
}

.doc-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.doc-icon .el-icon {
  color: white;
  font-size: 18px;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-meta {
  display: flex;
  gap: 8px;
}

.doc-status {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
}

.doc-status.completed {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

.doc-status.processing {
  color: #e6a23c;
  background: rgba(230, 162, 60, 0.1);
}

.doc-status.failed {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.doc-delete {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.document-item:hover .doc-delete {
  opacity: 1;
}

.ai-tools-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 4px;
}

.ai-tools-grid::-webkit-scrollbar {
  width: 4px;
}

.ai-tools-grid::-webkit-scrollbar-track {
  background: transparent;
}

.ai-tools-grid::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.2);
  border-radius: 2px;
}

.ai-tools-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.3);
}

.ai-tool-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: rgba(102, 126, 234, 0.03);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ai-tool-btn:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
}

.ai-tool-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ai-tool-btn.disabled:hover {
  transform: none;
}

.tool-icon {
  width: 32px;
  height: 32px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tool-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.main-area {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  height: 100%;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.02) 0%, rgba(255, 255, 255, 0) 100%);
  height: 100%;
  min-height: 0;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.08);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.chat-title .el-icon {
  color: var(--primary-color);
  font-size: 18px;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.chat-actions .el-button {
  color: var(--text-secondary);
  font-size: 13px;
}

.chat-actions .el-button:hover {
  color: var(--primary-color);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.2);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.3);
}

.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: messageIn 0.3s ease;
}

@keyframes messageIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-wrapper.streaming {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}

.message-avatar {
  flex-shrink: 0;
}

.avatar-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.avatar-icon.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.avatar-icon.assistant {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-wrapper.user .message-content {
  max-width: 70%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.message-role {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.streaming-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.streaming-indicator .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary-color);
  animation: streamingDot 1.4s ease-in-out infinite both;
}

.streaming-indicator .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.streaming-indicator .dot:nth-child(2) {
  animation-delay: -0.16s;
}

.streaming-indicator .dot:nth-child(3) {
  animation-delay: 0;
}

@keyframes streamingDot {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.message-text {
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  max-width: 100%;
}

.message-wrapper.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 6px;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.25);
}

.message-wrapper.user .message-text :deep(.markdown-link) {
  color: rgba(255, 255, 255, 0.9);
  border-bottom-color: rgba(255, 255, 255, 0.5);
}

.message-wrapper.user .message-text :deep(.markdown-link:hover) {
  background: rgba(255, 255, 255, 0.15);
}

.message-wrapper.assistant .message-text {
  background: #fff;
  border: 1px solid rgba(102, 126, 234, 0.12);
  border-bottom-left-radius: 6px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
}

.message-wrapper.streaming .message-text {
  border-color: rgba(102, 126, 234, 0.2);
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.1);
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
  flex: 1;
  min-height: 0;
}

.welcome-icon {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  animation: float 4s ease-in-out infinite;
}

.welcome-icon .el-icon {
  font-size: 32px;
  color: white;
}

.welcome-message h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.welcome-message p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 28px;
  max-width: 320px;
}

.suggestion-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  width: 100%;
  max-width: 500px;
}

.suggestion-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.04) 0%, rgba(118, 75, 162, 0.04) 100%);
  border: 1px solid rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.suggestion-card:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-color: rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.12);
}

.suggestion-card .el-icon {
  font-size: 20px;
  color: var(--primary-color);
}

.suggestion-card span {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.chat-input-wrapper {
  flex-shrink: 0;
  padding: 16px 20px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.input-container {
  position: relative;
}

.input-box {
  position: relative;
  display: flex;
  align-items: flex-end;
  background: #fff;
  border: 2px solid rgba(102, 126, 234, 0.15);
  border-radius: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.input-box:focus-within {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.chat-textarea {
  flex: 1;
  min-height: 80px;
  max-height: 200px;
  padding: 14px 16px;
  padding-right: 60px;
  border: none;
  outline: none;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  background: transparent;
  color: var(--text-primary);
  font-family: inherit;
}

.chat-textarea::placeholder {
  color: var(--text-tertiary);
}

.chat-textarea:disabled {
  background: rgba(0, 0, 0, 0.02);
  cursor: not-allowed;
}

.send-btn-inline {
  position: absolute;
  right: 12px;
  bottom: 12px;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 18px;
}

.send-btn-inline:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn-inline:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.input-hint {
  margin-top: 10px;
  text-align: right;
}

.input-hint span {
  font-size: 12px;
  color: var(--text-tertiary);
}

.upload-area {
  padding: 8px 0;
}

.upload-component {
  margin-bottom: 16px;
}

.upload-icon {
  font-size: 48px;
  color: var(--primary-color);
  margin-bottom: 16px;
}

.upload-text {
  text-align: center;
}

.primary-text {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.primary-text em {
  color: var(--primary-color);
  font-style: normal;
}

.hint-text {
  font-size: 14px;
  color: var(--text-tertiary);
}

.limit-text {
  font-size: 12px;
  color: var(--primary-color);
  margin-top: 8px;
  font-weight: 500;
}

.upload-limit-warning {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  background: rgba(245, 108, 108, 0.05);
  border: 1px dashed rgba(245, 108, 108, 0.3);
  border-radius: 12px;
  color: #f56c6c;
}

.upload-limit-warning .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-limit-warning span {
  font-size: 14px;
  line-height: 1.6;
  max-width: 280px;
}

.file-preview {
  margin-top: 16px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-info .el-icon {
  font-size: 24px;
  color: var(--primary-color);
}

.file-info span {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.content-result-section {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  z-index: 10;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.result-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.result-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.result-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.result-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.result-body::-webkit-scrollbar {
  width: 6px;
}

.result-body::-webkit-scrollbar-track {
  background: transparent;
}

.result-body::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.2);
  border-radius: 3px;
}

.result-body::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.3);
}

.result-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary);
}

:deep(.markdown-paragraph) {
  margin: 0 0 12px 0;
  line-height: 1.75;
  color: var(--text-primary);
}

:deep(.markdown-h1) {
  font-size: 1.5em;
  font-weight: 700;
  color: var(--text-primary);
  margin: 1.5em 0 0.75em 0;
  padding-bottom: 0.4em;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
  line-height: 1.3;
}

:deep(.markdown-h2) {
  font-size: 1.3em;
  font-weight: 600;
  color: var(--text-primary);
  margin: 1.25em 0 0.6em 0;
  padding-bottom: 0.3em;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
  line-height: 1.35;
}

:deep(.markdown-h3) {
  font-size: 1.15em;
  font-weight: 600;
  color: var(--text-primary);
  margin: 1em 0 0.5em 0;
  line-height: 1.4;
}

:deep(.markdown-h4) {
  font-size: 1em;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0.8em 0 0.4em 0;
  line-height: 1.4;
}

:deep(.markdown-list) {
  margin: 0.75em 0;
  padding-left: 1.5em;
  list-style: none !important;
}

:deep(.markdown-li) {
  position: relative;
  margin: 0.4em 0;
  line-height: 1.65;
  padding-left: 0.3em;
  list-style: none !important;
}

:deep(.markdown-li)::before {
  content: '•';
  position: absolute;
  left: -1em;
  color: #667eea;
  font-weight: bold;
}

:deep(.markdown-li-ordered)::before {
  content: '';
}

:deep(.markdown-bold) {
  font-weight: 600;
  color: var(--text-primary);
}

:deep(.markdown-italic) {
  font-style: italic;
  color: var(--text-secondary);
}

:deep(.markdown-bold-italic) {
  font-style: italic;
  color: var(--text-primary);
}

:deep(.markdown-inline-code) {
  padding: 0.15em 0.4em;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid rgba(102, 126, 234, 0.15);
  border-radius: 4px;
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', Monaco, Consolas, monospace;
  font-size: 0.9em;
  color: #667eea;
  white-space: nowrap;
}

:deep(.code-block) {
  margin: 1em 0;
  border-radius: 10px;
  overflow: hidden;
  background: #1e1e2e;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

:deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.code-lang) {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

:deep(.copy-code-btn) {
  padding: 4px 10px;
  background: rgba(102, 126, 234, 0.3);
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;
}

:deep(.copy-code-btn:hover) {
  background: rgba(102, 126, 234, 0.5);
}

:deep(.markdown-pre) {
  margin: 0;
  padding: 16px;
  background: transparent;
  overflow-x: auto;
}

:deep(.markdown-pre code) {
  font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', Monaco, Consolas, monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #cdd6f4;
  white-space: pre;
}

:deep(.markdown-link) {
  color: #667eea;
  text-decoration: none;
  border-bottom: 1px dashed rgba(102, 126, 234, 0.5);
  transition: all 0.2s ease;
  padding-bottom: 1px;
}

:deep(.markdown-link:hover) {
  color: #764ba2;
  border-bottom-color: #764ba2;
  background: rgba(102, 126, 234, 0.08);
}

.generating-section {
  margin-top: 24px;
  padding: 60px 20px;
  text-align: center;
  border-radius: 12px;
}

.generating-animation {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.generating-animation .dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  animation: generatingDots 1.4s ease-in-out infinite both;
}

.generating-animation .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.generating-animation .dot:nth-child(2) {
  animation-delay: -0.16s;
}

.generating-animation .dot:nth-child(3) {
  animation-delay: 0;
}

@keyframes generatingDots {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.generating-section p {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@media (max-width: 1024px) {
  .detail-content {
    grid-template-columns: 1fr;
  }

  .sidebar {
    min-width: auto;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .sidebar-card {
    flex: 1;
    min-width: 280px;
  }

  .suggestion-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .back-btn {
    position: absolute;
    left: 20px;
  }

  .notebook-title {
    font-size: 20px;
  }

  .message-content {
    max-width: 85%;
  }

  .sidebar {
    flex-direction: column;
  }

  .ai-tools-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}
</style>
