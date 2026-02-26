<template>
  <div class="notebooks-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="title-text">我的</span>
          <span class="title-gradient">笔记本</span>
        </h1>
        <p class="hero-subtitle">创建、管理和探索您的知识库</p>
      </div>
      
      <div class="hero-actions">
        <button class="create-btn" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          <span>新建笔记本</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-section">
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <el-icon><Notebook /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ notebooks.length }}</div>
          <div class="stat-label">笔记本总数</div>
        </div>
      </div>
      
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalDocuments }}</div>
          <div class="stat-label">文档总数</div>
        </div>
      </div>
      
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalMessages }}</div>
          <div class="stat-label">对话总数</div>
        </div>
      </div>
    </div>

    <!-- Notebooks Grid -->
    <div class="notebooks-section">
      <div class="section-header">
        <h2 class="section-title">最近笔记本</h2>
        <div class="section-actions">
          <el-input
            v-model="searchQuery"
            placeholder="搜索笔记本..."
            :prefix-icon="Search"
            clearable
            class="search-input"
          />
        </div>
      </div>

      <div class="notebooks-grid" v-loading="loading">
        <transition-group name="scale">
          <div
            v-for="notebook in filteredNotebooks"
            :key="notebook.id"
            class="notebook-card glass-card"
            @click="goToNotebook(notebook.id)"
          >
            <div class="card-header">
              <div class="notebook-icon-container">
                <el-icon class="notebook-icon"><Notebook /></el-icon>
                <div class="icon-glow"></div>
                
              </div>
              <div class="card-menu">
                 <h3 class="notebook-name">{{ notebook.name || '未命名笔记本' }}</h3>
              </div>
            </div>
            
            <div class="card-body">
             
              <p v-if="notebook.description" class="notebook-description">{{ notebook.description }}</p>
              
              <div class="card-meta">
                <div class="meta-item">
                  <el-icon><Document /></el-icon>
                  <span>{{ notebook.document_count || 0 }} 文档</span>
                </div>
                <div class="meta-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatDate(notebook.created_at) }}</span>
                </div>
              </div>
            </div>

            <div class="card-footer">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: getProgress(notebook) }"></div>
              </div>
            </div>
          </div>
        </transition-group>

        <el-empty
          v-if="!loading && notebooks.length === 0"
          description="暂无笔记本"
          :image-size="120"
        >
          <template #description>
            <p class="empty-text">还没有创建任何笔记本</p>
            <p class="empty-hint">点击上方按钮创建您的第一个笔记本</p>
          </template>
          <el-button type="primary" @click="showCreateDialog = true" class="empty-btn">
            <el-icon><Plus /></el-icon>
            立即创建
          </el-button>
        </el-empty>

        <el-empty
          v-if="!loading && notebooks.length > 0 && filteredNotebooks.length === 0"
          description="未找到匹配的笔记本"
          :image-size="120"
        />
      </div>
    </div>

    <!-- Create Notebook Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新笔记本"
      width="500px"
      class="create-dialog"
    >
      <div class="dialog-content">
        <el-form :model="form" label-width="80px" class="create-form">
          <el-form-item label="名称" required>
            <el-input
              v-model="form.name"
              placeholder="输入笔记本名称"
              size="large"
              :prefix-icon="Edit"
            />
          </el-form-item>
          
          <el-form-item label="描述">
            <el-input
              v-model="form.description"
              type="textarea"
              placeholder="添加描述（可选）"
              :rows="4"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>
        
        <div class="template-section">
          <div class="section-label">选择模板</div>
          <div class="template-grid">
            <div class="template-item active">
              <el-icon><Document /></el-icon>
              <span>空白</span>
            </div>
            <div class="template-item">
              <el-icon><Reading /></el-icon>
              <span>学习笔记</span>
            </div>
            <div class="template-item">
              <el-icon><Briefcase /></el-icon>
              <span>工作文档</span>
            </div>
            <div class="template-item">
              <el-icon><Notebook /></el-icon>
              <span>研究项目</span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="createNotebook"
            :loading="creating"
            size="large"
            class="confirm-btn"
          >
            <el-icon><Check /></el-icon>
            创建笔记本
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Notebook,
  Document,
  Search,
  MoreFilled,
  Clock,
  Edit,
  Check,
  ChatDotRound,
  Reading,
  Briefcase
} from '@element-plus/icons-vue'
import { notebooksApi } from '../api/notebooks'

const router = useRouter()
const loading = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const searchQuery = ref('')

const notebooks = ref<any[]>([])
const totalDocuments = ref(0)
const totalMessages = ref(0)

const form = ref({
  name: '',
  description: ''
})

const filteredNotebooks = computed(() => {
  if (!searchQuery.value) {
    return notebooks.value
  }
  const query = searchQuery.value.toLowerCase()
  return notebooks.value.filter(notebook =>
    notebook.name?.toLowerCase().includes(query) ||
    (notebook.description && notebook.description.toLowerCase().includes(query))
  )
})

const loadNotebooks = async () => {
  loading.value = true
  try {
    const result = await notebooksApi.list()
    console.log('Loaded notebooks:', result)
    notebooks.value = Array.isArray(result) ? result : []
    // 模拟统计数据
    totalDocuments.value = notebooks.value.reduce((sum, nb) => sum + (nb.document_count || 0), 0)
    totalMessages.value = notebooks.value.reduce((sum, nb) => sum + (nb.message_count || 0), 0)
  } catch (error) {
    console.error('Load notebooks error:', error)
    ElMessage.error('加载笔记本失败')
    notebooks.value = []
  } finally {
    loading.value = false
  }
}

const createNotebook = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入笔记本名称')
    return
  }
  
  creating.value = true
  try {
    await notebooksApi.create(form.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    form.value = { name: '', description: '' }
    await loadNotebooks()
  } catch (error) {
    console.error('Create notebook error:', error)
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const goToNotebook = (id: number) => {
  router.push(`/notebook/${id}`)
}

const formatDate = (date: string) => {
  if (!date) return '未知时间'
  
  // 尝试解析日期
  const target = new Date(date)
  
  // 检查日期是否有效
  if (isNaN(target.getTime())) {
    return '未知时间'
  }
  
  const now = new Date()
  const diff = now.getTime() - target.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days} 天前`
  if (days < 30) return `${Math.floor(days / 7)} 周前`
  
  // 返回格式化的日期 MM-DD
  return `${String(target.getMonth() + 1).padStart(2, '0')}-${String(target.getDate()).padStart(2, '0')}`
}

const getProgress = (notebook: any) => {
  // 模拟进度计算
  return Math.min(100, (notebook.document_count || 0) * 10 + 10) + '%'
}

onMounted(() => {
  loadNotebooks()
})
</script>

<style scoped>
.notebooks-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
  animation: fadeIn 0.5s ease;
  min-height: calc(100vh - 120px);
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

/* Hero Section */
.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 0;
}

.hero-title {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.title-text {
  color: var(--text-primary);
}

.title-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 400;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.create-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.create-btn:hover::before {
  width: 200%;
  height: 200%;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.create-btn:active {
  transform: translateY(-1px);
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  cursor: default;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: float 4s ease-in-out infinite;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
  font-weight: 500;
}

/* Notebooks Section */
.notebooks-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.search-input {
  width: 260px;
}

.notebooks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  min-height: 200px;
}

.notebook-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.notebook-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.notebook-card:hover::before {
  opacity: 1;
}

.notebook-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.15);
}

.card-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.notebook-icon-container {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.notebook-icon {
  font-size: 18px;
  color: var(--primary-color);
  z-index: 1;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 70%;
  height: 70%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 3s ease-in-out infinite;
}

.card-menu {
  opacity: 0.8;
  transition: opacity 0.3s ease;
  text-align: left;
  padding-left: 12px;
  overflow: hidden;
}

.notebook-card:hover .card-menu {
  opacity: 1;
}

.menu-icon {
  font-size: 16px;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.menu-icon:hover {
  color: var(--primary-color);
  background: rgba(102, 126, 234, 0.1);
}

.card-body {
  flex: 1;
  padding-bottom: 6px;
  display: flex;
  flex-direction: column;
}

.notebook-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
  letter-spacing: -0.01em;
}

.notebook-description {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  min-height: 0;
}

.card-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.meta-item .el-icon {
  font-size: 12px;
}

.card-footer {
  padding-top: 6px;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
}

.progress-bar {
  height: 3px;
  background: var(--bg-tertiary);
  border-radius: 1.5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 1.5px;
  transition: width 0.5s ease;
}

/* Empty State */
.empty-text {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: 24px;
}

.empty-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 12px 24px;
  font-weight: 600;
}

/* Dialog Styles */
.dialog-content {
  padding: 8px 0;
}

.create-form {
  margin-bottom: 24px;
}

.template-section {
  margin-top: 24px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.template-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-item .el-icon {
  font-size: 24px;
  color: var(--text-tertiary);
}

.template-item span {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.template-item:hover {
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.2);
}

.template-item.active {
  background: rgba(102, 126, 234, 0.1);
  border-color: var(--primary-color);
}

.template-item.active .el-icon {
  color: var(--primary-color);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.confirm-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
}

/* Animations */
.scale-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

.scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Responsive */
@media (max-width: 768px) {
  .notebooks-page {
    padding: 10px;
  }

  .hero-section {
    flex-direction: column;
    text-align: center;
    gap: 5px;
  }

  .hero-title {
    font-size: 32px;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .notebooks-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .template-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
