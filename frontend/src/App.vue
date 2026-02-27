<template>
  <div id="app">
    <div class="dynamic-bg"></div>
    <el-container style="height: 100vh">
      <!-- Header -->
      <el-header class="modern-header">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-container">
              <el-icon class="logo-icon" :size="28">
                <Notebook />
              </el-icon>
              <div class="logo-text">
                <span class="title">NotebookLM</span>
                <span class="subtitle">AI Powered</span>
              </div>
            </div>
          </div>

          <nav class="nav-section">
            <router-link to="/" custom v-slot="{ navigate, isActive }">
              <div
                :class="['nav-item', { active: isActive }]"
                @click="navigate"
              >
                <el-icon><Folder /></el-icon>
                <span>笔记本</span>
              </div>
            </router-link>
            <router-link to="/settings" custom v-slot="{ navigate, isActive }">
              <div
                :class="['nav-item', { active: isActive }]"
                @click="navigate"
              >
                <el-icon><Setting /></el-icon>
                <span>设置</span>
              </div>
            </router-link>
            <router-link to="/about" custom v-slot="{ navigate, isActive }">
              <div
                :class="['nav-item', { active: isActive }]"
                @click="navigate"
              >
                <el-icon><InfoFilled /></el-icon>
                <span>关于</span>
              </div>
            </router-link>
          </nav>

          <div class="header-actions">
           
          </div>
        </div>
      </el-header>

      <!-- Main Content -->
      <el-main class="modern-main" style="height: calc(100vh - 40px); overflow-y: auto; overflow-x: hidden;">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Notebook, Setting, Folder, InfoFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
#app {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* Modern Header */
.modern-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.08);
  padding: 0 32px;
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1800px;
  margin: 0 auto;
}

/* Logo Section */
.logo-section {
  display: flex;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.logo-container:hover {
  background: rgba(102, 126, 234, 0.08);
  transform: translateX(4px);
}

.logo-icon {
  color: var(--primary-color);
  animation: float 4s ease-in-out infinite;
  filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-tertiary);
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* Navigation */
.nav-section {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(102, 126, 234, 0.05);
  padding: 6px;
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
  opacity: 0;
  z-index: -1;
}

.nav-item:hover::before {
  width: 200%;
  height: 200%;
  opacity: 0.1;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.nav-item.active .el-icon {
  transform: scale(1.1);
}

.nav-item .el-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.nav-item:hover {
  transform: translateY(-2px);
  color: var(--primary-color);
}

.nav-item.active:hover {
  color: white;
}

/* Header Actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(79, 172, 254, 0.1);
  border-radius: 20px;
  border: 1px solid rgba(79, 172, 254, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 50%;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  box-shadow: 0 0 8px rgba(79, 172, 254, 0.5);
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Modern Main */
.modern-main {
  background: transparent;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Animations */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-4px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.8);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .modern-header {
    padding: 0 16px;
  }

  .logo-text .title {
    font-size: 20px;
  }

  .logo-text .subtitle {
    display: none;
  }

  .nav-item span {
    display: none;
  }

  .nav-item {
    padding: 10px;
  }

  .status-indicator {
    display: none;
  }
}
</style>
