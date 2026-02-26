<template>
  <div class="app-container">
      <!-- Header -->
      <header class="header">
        <h1 class="title">{{ title }}</h1>
        <div class="actions">
          <el-button-group>
            <el-button type="primary" @click="exportSVG" :disabled="!hasContent">
              <el-icon><Download /></el-icon>
              导出 SVG
            </el-button>
          </el-button-group>
        </div>
      </header>
        <!-- Mindmap Container -->
        <div class="mindmap-wrapper">
          <svg ref="svgRef" class="mindmap-svg"></svg>
        </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Close } from '@element-plus/icons-vue'
import { Transformer } from 'markmap-lib'
import { Markmap } from 'markmap-view'

// 定义组件属性
const props = defineProps({
  markdown: {
    type: [String, Object],
    default: ''
  }
})

// 响应式状态
const svgRef = ref(null)
const title = ref('脑图渲染器')
const markdownContent = ref('')
const markmapInstance = ref(null)

// 计算属性
const hasContent = computed(() => !!markdownContent.value )

// 处理 Markdown 内容
function processMarkdown(content) {
  let rawContent = ''
  
  // 如果 content 是 JSON 对象，提取 data 字段
  if (content && typeof content === 'object') {
    rawContent = content.data || ''
  } else {
    // 兼容字符串形式，尝试解析 JSON 或直接使用
    try {
      const parsed = JSON.parse(content)
      rawContent = (parsed && typeof parsed === 'object' && parsed.data) ? parsed.data : content
    } catch (e) {
      rawContent = content || ''
    }
  }

  let processed = String(rawContent).trim()
  console.log('原始 Markdown 内容:', processed)
  
  // 检查是否有一级标题
  const hasH1 = /^#\s+.+/m.test(processed)
  if (!hasH1 && processed) {
    processed = '# 未命名脑图\n\n' + processed
    ElMessage.warning('Markdown 缺少一级标题，已自动添加"未命名脑图"作为中心节点')
  }
  
  // 提取一级标题作为页面标题
  const h1Match = processed.match(/^#\s+(.+)/m)
  if (h1Match) {
    title.value = h1Match[1].trim()
  }
  
  return processed
}

// 渲染脑图
async function renderMindmap(content) {
  debugger
  if (!content) return
  debugger
  try { 
    const transformer = new Transformer()
    const { root } = transformer.transform(content)
    
    // 清空之前的内容
    svgRef.value.innerHTML = ''
    
    // 创建 Markmap 实例
    markmapInstance.value = Markmap.create(svgRef.value, {
      autoFit: true,
      duration: 500,
      maxWidth: 300,
      spacingHorizontal: 80,
      spacingVertical: 10,
      paddingX: 20
    }, root)
  } catch (err) {
    ElMessage.error('脑图渲染失败: ' + err.message)
  } finally {
    
  }
}

// 导出 SVG
function exportSVG() {
  if (!svgRef.value) return
  
  try {
    const svgElement = svgRef.value.cloneNode(true)
    svgElement.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
    
    const svgData = new XMLSerializer().serializeToString(svgElement)
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    
    downloadFile(url, `${title.value || Date.now()}.svg`)
    URL.revokeObjectURL(url)
    
    ElMessage.success('SVG 导出成功')
  } catch (err) {
    ElMessage.error('SVG 导出失败: ' + err.message)
  }
}

// 下载文件
function downloadFile(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 监听 markdown 属性变化
watch(() => props.markdown, (newValue) => {
  debugger
  if (!newValue) return
  markdownContent.value = processMarkdown(newValue)
  renderMindmap(markdownContent.value)
}, {
  deep: true // 添加深度监听，确保对象内部属性变化也能被监听到
})

// 组件挂载后初始化
onMounted(() => {
  if (props.markdown) {
    markdownContent.value = processMarkdown(props.markdown)
    renderMindmap(markdownContent.value)
  }
})

// 监听窗口大小变化
window.addEventListener('resize', () => {
  if (markmapInstance.value) {
    markmapInstance.value.fit()
  }
})
</script>

<style>
.app-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
}
.header {
  display: flex;
  align-items: center;
  width: 100%;
  justify-content: space-between;
  padding: 5px 5px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(to bottom, #ffffff, #f5f7fa);
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.actions {
  display: flex;
  gap: 8px;
}

.mindmap-wrapper {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.mindmap-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* Markmap 样式覆盖 */
.mindmap-svg .markmap-node text {
  font-size: 14px;
}

.mindmap-svg .markmap-link {
  stroke: #409eff;
  stroke-width: 2px;
}
</style>
