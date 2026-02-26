<template>
  <div class="settings-page">
    
    <div class="settings-layout">
      <div class="settings-sidebar glass-card">
        <div class="sidebar-menu">
          <div
            v-for="tab in tabs"
            :key="tab.key"
            :class="['menu-item', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            <el-icon class="menu-icon">
              <component :is="tab.icon" />
            </el-icon>
            <span class="menu-text">{{ tab.label }}</span>
          </div>
        </div>
      </div>

      <div class="settings-content glass-card">
        <div v-if="activeTab === 'llm'" class="content-section">
          <div class="section-header">
            <div class="section-info">
              <h2>LLM 配置</h2>
              <p>配置大语言模型的参数和连接信息</p>
            </div>
            <button class="reset-btn" @click="resetConfig">
              <el-icon>
                <RefreshLeft />
              </el-icon>
              <span>重置默认</span>
            </button>
          </div>

          <div class="config-form">
            <div class="form-group">
              <label class="form-label">
                <span class="label-text">模型名称</span>
              </label>
              <el-input v-model="config.modelName" placeholder="例如: GPT-4, Claude-3" size="large" clearable />
              <p class="form-hint">显示在界面上的模型名称</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">Model ID</span>
              </label>
              <el-input v-model="config.modelId" placeholder="例如: gpt-4, claude-3-opus-20240229" size="large" clearable />
              <p class="form-hint">实际调用的模型标识符</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">Base URL</span>
              </label>
              <el-input v-model="config.baseUrl" placeholder="例如: https://api.openai.com/v1" size="large" clearable />
              <p class="form-hint">API 基础地址，通常以 /v1 结尾</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">API Key</span>
              </label>
              <el-input v-model="config.apiKey" placeholder="sk-..." size="large" type="password" show-password
                clearable />
              <p class="form-hint">API 访问密钥，请妥善保管</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">Temperature</span>
                <span class="label-value">{{ config.temperature }}</span>
              </label>
              <div class="slider-container">
                <el-slider v-model="config.temperature" :min="0" :max="2" :step="0.1" :marks="temperatureMarks"
                  show-input />
              </div>
              <p class="form-hint">控制输出随机性：0-0.3 精确，0.7-0.9 平衡，1.0-2.0 创意</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">Max Tokens</span>
                <span class="label-value">{{ config.maxTokens }}</span>
              </label>
              <el-input-number v-model="config.maxTokens" :min="100" :max="16384" :step="100" size="large" />
              <p class="form-hint">控制生成内容的最大长度，单位为令牌数</p>
            </div>

            <div class="form-actions">
              <button class="save-btn" @click="saveConfig" :disabled="saving">
                <el-icon v-if="!saving">
                  <Check />
                </el-icon>
                <el-icon v-else class="is-loading">
                  <Loading />
                </el-icon>
                <span>{{ saving ? '保存中...' : '保存配置' }}</span>
              </button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'doubao'" class="content-section">
          <div class="section-header">
            <div class="section-info">
              <h2>豆包语音播客配置</h2>
              <p>配置豆包语音合成服务参数</p>
            </div>
            <button class="reset-btn" @click="resetDoubaoConfig">
              <el-icon>
                <RefreshLeft />
              </el-icon>
              <span>重置默认</span>
            </button>
          </div>

          <div class="config-form">
            <div class="form-group">
              <label class="form-label">
                <span class="label-text">APP ID</span>
              </label>
              <el-input v-model="doubaoConfig.appId" placeholder="请输入豆包应用ID" size="large" clearable />
              <p class="form-hint">豆包语音服务的应用标识符</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">Access Token</span>
              </label>
              <el-input v-model="doubaoConfig.accessToken" placeholder="请输入访问令牌" size="large" type="password"
                show-password clearable />
              <p class="form-hint">豆包语音服务的访问令牌</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">Secret Key</span>
              </label>
              <el-input v-model="doubaoConfig.secretKey" placeholder="请输入密钥" size="large" type="password"
                show-password clearable />
              <p class="form-hint">豆包语音服务的密钥</p>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-text">发音人选择</span>
                <span class="label-value" v-if="doubaoConfig.speakers.length > 0">
                  已选 {{ doubaoConfig.speakers.length }} 个
                </span>
              </label>
              <el-select v-model="doubaoConfig.speakers" multiple placeholder="请选择发音人（必须选择2个）" size="large"
                style="width: 100%">
                <el-option v-for="item in speakerOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
              <p class="form-hint">选择2个发音人用于播客对话（建议选择一男一女）</p>
            </div>

            <div class="form-actions">
              <button class="save-btn" @click="saveConfig" :disabled="saving">
                <el-icon v-if="!saving">
                  <Check />
                </el-icon>
                <el-icon v-else class="is-loading">
                  <Loading />
                </el-icon>
                <span>{{ saving ? '保存中...' : '保存配置' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, RefreshLeft, Check, Loading, Cpu, Headset } from '@element-plus/icons-vue'
import { configApi } from '../api/config'

const saving = ref(false)
const activeTab = ref('llm')

const tabs = [
  { key: 'llm', label: 'LLM 配置', icon: Cpu },
  { key: 'doubao', label: '豆包语音播客', icon: Headset }
]

const temperatureMarks = {
  0: { label: '精确', style: { color: '#8a8aaa' } },
  0.7: { label: '平衡', style: { color: '#8a8aaa' } },
  1: { label: '创意', style: { color: '#8a8aaa' } },
  2: { label: '自由', style: { color: '#8a8aaa' } }
}

const config = ref({
  modelName: 'deepseek-chat',
  modelId: 'deepseek-chat',
  baseUrl: 'https://api.deepseek.com',
  apiKey: 'sk-...',
  temperature: 0.7,
  maxTokens: 8000
})

const speakerOptions = [
  { value: 'zh_female_mizaitongxue_v2_saturn_bigtts', label: '女声-麦子同学' },
  { value: 'zh_male_dayixiansheng_v2_saturn_bigtts', label: '男声-大一先生' },
  { value: 'zh_male_liufei_v2_saturn_bigtts', label: '男声-刘飞' },
  { value: 'zh_male_xiaolei_v2_saturn_bigtts', label: '男声-小磊' }
]

const doubaoConfig = ref({
  appId: '',
  accessToken: '',
  secretKey: '',
  speakers: [] as string[]
})

const loadConfig = async () => {
  try {
    const configs = await configApi.list()

    const modelConfig = configs.find((c: any) => c.key === 'llm.model_name')
    const idConfig = configs.find((c: any) => c.key === 'llm.model_id')
    const urlConfig = configs.find((c: any) => c.key === 'llm.base_url')
    const keyConfig = configs.find((c: any) => c.key === 'llm.api_key')
    const tempConfig = configs.find((c: any) => c.key === 'llm.temperature')
    const maxTokensConfig = configs.find((c: any) => c.key === 'llm.max_tokens')

    if (modelConfig) config.value.modelName = modelConfig.value
    if (idConfig) config.value.modelId = idConfig.value
    if (urlConfig) config.value.baseUrl = urlConfig.value
    if (keyConfig) config.value.apiKey = keyConfig.value
    if (tempConfig) config.value.temperature = parseFloat(tempConfig.value)
    if (maxTokensConfig) config.value.maxTokens = parseInt(maxTokensConfig.value)

    const appIdConfig = configs.find((c: any) => c.key === 'doubao.app_id')
    const accessTokenConfig = configs.find((c: any) => c.key === 'doubao.access_token')
    const secretKeyConfig = configs.find((c: any) => c.key === 'doubao.secret_key')
    const speakersConfig = configs.find((c: any) => c.key === 'doubao.speakers')

    if (appIdConfig) doubaoConfig.value.appId = appIdConfig.value
    if (accessTokenConfig) doubaoConfig.value.accessToken = accessTokenConfig.value
    if (secretKeyConfig) doubaoConfig.value.secretKey = secretKeyConfig.value
    if (speakersConfig) {
      try {
        doubaoConfig.value.speakers = JSON.parse(speakersConfig.value)
      } catch {
        doubaoConfig.value.speakers = []
      }
    }
  } catch (error) {
    console.error('Load config error:', error)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await configApi.set('llm.model_name', config.value.modelName, '模型显示名称', 'llm')
    await configApi.set('llm.model_id', config.value.modelId, '实际调用的模型ID', 'llm')
    await configApi.set('llm.base_url', config.value.baseUrl, 'API基础地址', 'llm')
    await configApi.set('llm.api_key', config.value.apiKey, 'API访问密钥', 'llm')
    await configApi.set('llm.temperature', config.value.temperature.toString(), '控制输出随机性', 'llm')
    await configApi.set('llm.max_tokens', config.value.maxTokens.toString(), '最大令牌数', 'llm')

    await configApi.set('doubao.app_id', doubaoConfig.value.appId, '豆包应用ID', 'doubao')
    await configApi.set('doubao.access_token', doubaoConfig.value.accessToken, '豆包访问令牌', 'doubao')
    await configApi.set('doubao.secret_key', doubaoConfig.value.secretKey, '豆包密钥', 'doubao')
    await configApi.set('doubao.speakers', JSON.stringify(doubaoConfig.value.speakers), '发音人列表', 'doubao')

    ElMessage.success('保存成功')
  } catch (error) {
    console.error('Save config error:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetConfig = () => {
  config.value = {
    modelName: 'deepseek-chat',
    modelId: 'deepseek-chat',
    baseUrl: 'https://api.deepseek.com',
    apiKey: 'sk-...',
    temperature: 0.7,
    maxTokens: 8000
  }
  ElMessage.info('已重置为默认值')
}

const resetDoubaoConfig = () => {
  doubaoConfig.value = {
    appId: '',
    accessToken: '',
    secretKey: '',
    speakers: []
  }
  ElMessage.info('已重置豆包配置为默认值')
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.settings-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
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

.page-header {
  margin-bottom: 32px;
  padding: 32px 0;
}

.header-content {
  text-align: center;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 12px;
}

.title-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  animation: float 4s ease-in-out infinite;
}

.title-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
}

.settings-layout {
  display: flex;
  gap: 24px;
  min-height: 600px;
}

.settings-sidebar {
  width: 260px;
  flex-shrink: 0;
  padding: 24px 16px;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 500;
}

.menu-item:hover {
  background: rgba(102, 126, 234, 0.08);
  color: var(--text-primary);
}

.menu-item.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  color: var(--primary-color);
  font-weight: 600;
}

.menu-icon {
  font-size: 20px;
}

.menu-text {
  flex: 1;
}

.settings-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

.content-section {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.section-info h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.section-info p {
  font-size: 15px;
  color: var(--text-secondary);
}

.reset-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(250, 112, 154, 0.1);
  border: 1px solid rgba(250, 112, 154, 0.2);
  border-radius: 12px;
  color: #fa709a;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  background: rgba(250, 112, 154, 0.15);
  border-color: rgba(250, 112, 154, 0.3);
  transform: translateY(-2px);
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.label-text {
  flex: 1;
}

.label-value {
  padding: 6px 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 600;
}

.form-hint {
  font-size: 13px;
  color: var(--text-tertiary);
  margin: 0;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.slider-container {
  padding: 16px 0;
}

:deep(.el-slider__runway) {
  background: rgba(102, 126, 234, 0.1);
  height: 8px;
}

:deep(.el-slider__bar) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

:deep(.el-slider__button) {
  border: 4px solid #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

:deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

:deep(.el-select__tags) {
  flex-wrap: wrap;
}

:deep(.el-tag) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  color: var(--primary-color);
}

.form-actions {
  display: flex;
  justify-content: center;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  margin-top: 16px;
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 16px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

.save-btn:active:not(:disabled) {
  transform: translateY(-1px);
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.save-btn .el-icon {
  font-size: 20px;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-4px);
  }
}

@media (max-width: 900px) {
  .settings-layout {
    flex-direction: column;
  }

  .settings-sidebar {
    width: 100%;
    padding: 16px;
  }

  .sidebar-menu {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .menu-item {
    flex-shrink: 0;
    padding: 12px 20px;
  }

  .settings-content {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .settings-page {
    padding: 16px;
  }

  .page-header {
    padding: 24px 0;
  }

  .page-title {
    font-size: 28px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .save-btn {
    width: 100%;
    padding: 14px 32px;
  }
}
</style>
