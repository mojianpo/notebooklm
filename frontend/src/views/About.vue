<template>
  <div class="about-page">
      <!-- Description Section -->
    <div class="description-section glass-card">
      <h2 class="section-title">关于 NotebookLM</h2>
      <p class="description-text">
        一个类似 Google NotebookLM 的智能笔记工作助手，支持文档管理、AI 问答和多种 AI 内容生成功能。
        帮助您更高效地组织知识、理解文档内容，并通过 AI 辅助学习。
      </p>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card glass-card">
          <div class="feature-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <h3 class="feature-title">笔记本管理</h3>
          <p class="feature-desc">创建和管理多个笔记本，灵活组织您的知识库</p>
        </div>

        <div class="feature-card glass-card">
          <div class="feature-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon><Upload /></el-icon>
          </div>
          <h3 class="feature-title">文档上传</h3>
          <p class="feature-desc">支持 PDF、DOCX、TXT、Markdown、HTML 多种格式</p>
        </div>

        <div class="feature-card glass-card">
          <div class="feature-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h3 class="feature-title">AI 知识问答</h3>
          <p class="feature-desc">基于文档的智能问答，流式输出，实时响应</p>
        </div>

        <div class="feature-card glass-card">
          <div class="feature-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon><MagicStick /></el-icon>
          </div>
          <h3 class="feature-title">内容生成</h3>
          <p class="feature-desc">8 种 AI 生成功能：报告、思维导图、闪卡等</p>
        </div>

        <div class="feature-card glass-card">
          <div class="feature-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon><Document /></el-icon>
          </div>
          <h3 class="feature-title">文档分析</h3>
          <p class="feature-desc">深度理解文档内容，提取关键信息</p>
        </div>

        <div class="feature-card glass-card">
          <div class="feature-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon><Reading /></el-icon>
          </div>
          <h3 class="feature-title">学习辅助</h3>
          <p class="feature-desc">生成测验、学习笔记，助力学习进步</p>
        </div>
      </div>
    </div>

    <!-- Tech Stack Section -->
    <div class="tech-section glass-card">
      <h2 class="section-title">技术栈</h2>
      <div class="tech-tags">
        <div class="tech-tag">
          <el-icon><Cpu /></el-icon>
          <span>Python 3.12</span>
        </div>
        <div class="tech-tag">
          <el-icon><Lightning /></el-icon>
          <span>FastAPI</span>
        </div>
        <div class="tech-tag">
          <el-icon><Monitor /></el-icon>
          <span>Vue 3</span>
        </div>
        <div class="tech-tag">
          <el-icon><Operation /></el-icon>
          <span>TypeScript</span>
        </div>
        <div class="tech-tag">
          <el-icon><Star /></el-icon>
          <span>Element Plus</span>
        </div>
        <div class="tech-tag">
          <el-icon><MagicStick /></el-icon>
          <span>langchain</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <p>© 2026 NotebookLM. All rights reserved.</p>
      <p>Built with AI</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Notebook,
  FolderOpened,
  Upload,
  ChatDotRound,
  MagicStick,
  Document,
  Reading,
  Cpu,
  Lightning,
  Monitor,
  Operation,
  Star
} from '@element-plus/icons-vue'
</script>

<style scoped>
.about-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
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

/* Hero Section */
.about-hero {
  text-align: center;
  margin-bottom: 64px;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-bg {
  width: 160px;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  box-shadow: 0 24px 64px rgba(102, 126, 234, 0.3);
  animation: float 4s ease-in-out infinite;
}

.logo-bg .el-icon {
  font-size: 80px;
  color: white;
}

.app-title {
  font-size: 56px;
  font-weight: 900;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
  letter-spacing: -2px;
}

.app-version {
  font-size: 20px;
  color: var(--text-tertiary);
  font-weight: 500;
  padding: 8px 24px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 24px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

/* Section Styles */
.section-title {
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 24px;
  text-align: center;
}

/* Description Section */
.description-section {
  padding: 40px;
  margin-bottom: 48px;
  text-align: center;
}

.description-text {
  font-size: 18px;
  line-height: 2;
  color: var(--text-secondary);
  max-width: 800px;
  margin: 0 auto;
}

/* Features Section */
.features-section {
  margin-bottom: 64px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.feature-card {
  padding: 32px;
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: white;
  font-size: 36px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.feature-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 15px;
  color: var(--text-tertiary);
  line-height: 1.8;
}

/* Tech Stack Section */
.tech-section {
  padding: 40px;
  margin-bottom: 48px;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
}

.tech-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(102, 126, 234, 0.08);
  border: 1px solid rgba(102, 126, 234, 0.15);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tech-tag:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

.tech-tag .el-icon {
  font-size: 18px;
  color: var(--primary-color);
}

/* Footer */
.footer {
  text-align: center;
  padding: 32px;
  border-top: 1px solid var(--border-color);
}

.footer p {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

/* Animations */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-12px);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .about-page {
    padding: 32px 16px;
  }

  .about-hero {
    margin-bottom: 48px;
  }

  .logo-bg {
    width: 120px;
    height: 120px;
  }

  .logo-bg .el-icon {
    font-size: 60px;
  }

  .app-title {
    font-size: 36px;
  }

  .app-version {
    font-size: 16px;
  }

  .section-title {
    font-size: 24px;
  }

  .description-section {
    padding: 24px;
  }

  .description-text {
    font-size: 16px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .tech-tags {
    flex-direction: column;
  }

  .tech-tag {
    justify-content: center;
  }
}
</style>
