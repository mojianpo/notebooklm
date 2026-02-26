# NotebookLM - AI 智能笔记助手

一个类似 Google NotebookLM 的智能笔记工作助手，支持文档管理、AI 问答、多种 AI 内容生成功能。

## 功能特性

### 核心功能
- **📚 笔记本管理** - 创建、管理多个知识库项目
- **📄 文档上传** - 支持 PDF、DOCX、TXT、Markdown、HTML 等格式
- **🤖 AI 知识问答** - 基于上传文档的智能问答，支持多轮对话（流式输出）
- **📝 文档解析** - 自动提取文档内容并建立索引

### AI 内容生成
- **📊 报告** - 自动生成结构化报告
- **🧠 思维导图** - 自动生成知识脑图结构
- **📋 闪卡** - 生成记忆卡片用于学习
- **❓ 测验** - 自动生成测试题目
- **🎧 播客脚本** - 将文档转换为对话式播客脚本
- **📽️ 演示文稿** - 生成演示文稿/PPT大纲
- **📈 数据表格** - 提取并整理结构化数据
- **🖼️ 信息图** - 可视化数据与概念

## 技术栈

### 后端
- **Python 3.12**
- **FastAPI** - 高性能 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **SQLite** - 轻量级数据库（可切换为 MySQL）
- **coze-coding-dev-sdk** - AI 能力支持（LLM 集成）

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Vite** - 构建工具

## 部署架构

本项目采用**一体化部署架构**，前端和后端在同一个端口上运行：

- **开发环境**：前端和后端分别运行（前端 5000 端口，后端 8000 端口）
- **生产环境**：前端构建为静态文件，由 FastAPI 统一服务（5000 端口）

### 部署流程说明

部署使用脚本自动化执行，所有脚本位于 `scripts/` 目录：

- `scripts/build-deploy.sh` - 构建脚本：安装依赖并构建前端
- `scripts/run-deploy.sh` - 运行脚本：安装后端依赖并启动服务
- `scripts/start-dev.sh` - 开发启动脚本：同时启动前后端

### 架构优势
- 简化部署流程，只需启动一个服务
- 减少跨域问题，前后端在同一域下
- 降低运维复杂度

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 24+
- pnpm 包管理器

### 安装依赖

#### 后端
```bash
cd backend
pip install -r ../requirements.txt
pip install coze-coding-dev-sdk
```

#### 前端
```bash
cd frontend
pnpm install
```

### 启动服务

#### 方式 1：使用 .coze 配置（推荐）
```bash
coze dev        # 开发环境（自动启动前后端）
coze build      # 生产环境构建
coze start      # 生产环境启动
```

#### 方式 2：使用部署脚本
```bash
# 开发环境
bash scripts/start-dev.sh

# 生产环境
bash scripts/build-deploy.sh  # 先构建
bash scripts/run-deploy.sh    # 再运行
```

#### 方式 3：手动启动

**开发环境**：
```bash
# 终端 1：启动后端
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 终端 2：启动前端
cd frontend
pnpm dev
```

**生产环境**：
```bash
# 1. 构建前端
cd frontend
pnpm build

# 2. 启动后端（会自动服务前端静态文件）
cd ../backend
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

### 访问应用
- **开发环境**：
  - 前端界面：http://localhost:5000
  - 后端 API 文档：http://localhost:8000/docs
  - 后端健康检查：http://localhost:8000/health

- **生产环境**：
  - 应用界面：http://localhost:5000
  - API 文档：http://localhost:5000/docs
  - 健康检查：http://localhost:5000/health

## 项目结构

```
.
├── backend/                # 后端 FastAPI 项目
│   ├── main.py            # 主应用入口（包含静态文件服务）
│   ├── static/            # 前端构建产物（自动生成）
│   ├── config.py          # 配置文件
│   ├── database.py        # 数据库配置
│   ├── models.py          # 数据库模型
│   ├── schemas.py         # Pydantic 模型
│   └── routers/           # API 路由
│       ├── notebooks.py   # 笔记本管理
│       ├── documents.py   # 文档管理
│       ├── chat.py        # AI 问答
│       └── content.py     # AI 内容生成
│
├── frontend/              # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/          # API 接口
│   │   ├── components/   # 公共组件
│   │   ├── router/       # 路由配置
│   │   ├── stores/       # Pinia 状态管理
│   │   └── views/        # 页面组件
│   │       ├── Notebooks.vue        # 笔记本列表
│   │       └── NotebookDetail.vue   # 笔记本详情
│   ├── vite.config.ts    # Vite 配置（构建输出到 backend/static）
│   └── package.json
│
├── .coze                  # Coze 配置文件
├── requirements.txt       # Python 依赖
└── README.md             # 项目文档
```

## API 端点

### 笔记本管理
- `POST /api/v1/notebooks/` - 创建笔记本
- `GET /api/v1/notebooks/` - 获取笔记本列表
- `GET /api/v1/notebooks/{id}` - 获取笔记本详情
- `DELETE /api/v1/notebooks/{id}` - 删除笔记本

### 文档管理
- `POST /api/v1/documents/upload/{notebook_id}` - 上传文档
- `DELETE /api/v1/documents/{document_id}` - 删除文档

### AI 问答（流式输出）
- `POST /api/v1/chat/` - AI 问答（SSE 流式输出）
- `GET /api/v1/chat/conversations/{notebook_id}` - 获取对话列表
- `GET /api/v1/chat/messages/{conversation_id}` - 获取消息列表

### AI 内容生成
- `POST /api/v1/content/generate` - 生成内容
- `GET /api/v1/content/types` - 获取支持的内容类型

## 使用说明

### 1. 创建笔记本
1. 点击"新建笔记本"按钮
2. 输入笔记本名称和描述
3. 点击"创建"

### 2. 上传文档
1. 进入笔记本详情页
2. 点击"上传文档"按钮
3. 拖拽或选择文件（支持 PDF、DOCX、TXT、MD、HTML）
4. 点击"上传"

### 3. AI 问答
1. 在笔记本详情页的聊天界面输入问题
2. 按 Ctrl + Enter 发送或点击"发送"按钮
3. AI 将基于上传的文档进行回答
4. 支持多轮对话

### 4. AI 内容生成
1. 在笔记本详情页左侧选择 AI 工具
2. 可选：添加自定义提示
3. 点击"开始生成"
4. 查看生成结果并复制

## 配置说明

### 数据库配置
默认使用 SQLite，配置文件位于 `backend/.env`：
```env
DATABASE_URL=sqlite:///./notebooklm.db
```

如需切换到 MySQL：
```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/notebooklm
```

### CORS 配置
在 `backend/config.py` 中修改允许的跨域源（生产环境已默认允许所有来源）：
```python
CORS_ORIGINS: list = ["*"]  # 生产环境建议限制具体域名
```

### 前端构建配置
前端构建输出默认配置到 `backend/static` 目录，在 `frontend/vite.config.ts` 中：
```typescript
export default defineConfig({
  build: {
    outDir: '../backend/static',  // 构建输出到后端目录
    emptyOutDir: true
  }
})
```

## 注意事项

1. **文件上传限制**：默认最大上传文件大小为 10MB
2. **流式输出**：AI 问答使用 SSE 协议实现流式输出
3. **文档解析**：文档内容需要手动标记为 "completed" 状态才能被 AI 使用
4. **API 路径**：FastAPI 建议在路径末尾添加斜杠（如 `/api/v1/notebooks/`）
5. **构建前置**：生产环境启动前必须先运行 `cd frontend && pnpm build`

## 后续优化方向

- [ ] 文档自动解析功能
- [ ] 实时协作编辑
- [ ] 音频生成功能（播客脚本转音频）
- [ ] 思维导图可视化展示
- [ ] 更多 AI 内容生成模板
- [ ] 用户认证系统
- [ ] 笔记本导出功能
- [ ] AI 模型配置支持

## 部署说明

### 自动部署（推荐）

#### 使用 .coze
```bash
coze build  # 自动安装依赖、构建前端
coze start  # 启动后端服务（包含静态文件服务）
```

#### 使用脚本
```bash
# 一键构建和启动
bash scripts/build-deploy.sh && bash scripts/run-deploy.sh
```

### 手动部署
```bash
# 1. 安装后端依赖
pip install -r requirements.txt
pip install coze-coding-dev-sdk

# 2. 安装前端依赖
cd frontend
pnpm install

# 3. 构建前端
pnpm build

# 4. 启动后端
cd ../backend
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

### 部署脚本说明

#### build-deploy.sh
构建前端项目，执行以下步骤：
1. 安装前端依赖（`pnpm install`）
2. 构建前端（`pnpm build`）
3. 输出到 `backend/static/` 目录

#### run-deploy.sh
启动生产环境服务，执行以下步骤：
1. 安装后端依赖（`pip install -r requirements.txt`）
2. 安装 coze-coding-dev-sdk
3. 启动 FastAPI 服务（端口 5000）

#### start-dev.sh
启动开发环境，执行以下步骤：
1. 安装前端依赖
2. 安装后端依赖
3. 启动后端服务（端口 8000，后台运行）
4. 启动前端服务（端口 5000）

## 许可证

MIT License
