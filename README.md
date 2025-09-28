# AI 角色扮演网站 · MVP

> **cyber-校招-2025** - 基于语音交互的 AI 角色扮演平台

## 📋 目录

- [项目概述](#项目概述)
- [产品定位](#产品定位)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [详细安装指南](#详细安装指南)
- [API 文档](#api-文档)
- [数据库设计](#数据库设计)
- [开发分工](#开发分工)
- [项目规划](#项目规划)
- [技术难点](#技术难点)
- [未来扩展](#未来扩展)

## 📚 项目文档

- **[📋 文档目录](./docs/README.md)** - 完整的文档结构和使用指南
- **[🚀 详细安装指南](./docs/SETUP_GUIDE.md)** - 完整的环境搭建和运行说明
- **[🏗️ 系统架构文档](./docs/ARCHITECTURE.md)** - 技术架构和模块设计详解
- **[👥 开发流程文档](./docs/DEVELOPMENT_WORKFLOW.md)** - 团队协作和开发规范
- **[📊 API 接口文档](#api-接口文档)** - RESTful API 详细说明

> 💡 **新团队成员建议阅读顺序**: [项目概述](#项目概述) → [快速开始](#快速开始) → [详细安装指南](./docs/SETUP_GUIDE.md) → [开发流程文档](./docs/DEVELOPMENT_WORKFLOW.md)

## 🎯 项目概述

### 目标

开发一个简洁的 Web 原型，用户能选择角色（如哈利波特 / 蜘蛛侠），并通过语音与其聊天（语音输入 → AI 回复 → 语音输出）。

### 核心价值

为影视/动漫爱好者、语言学习者、娱乐用户提供沉浸式互动体验。

### 目标用户

- **青少年与二次元/影视爱好者**：想和自己喜欢的角色互动
- **英语学习者**：借助角色扮演提升口语表达
- **娱乐用户**：想体验沉浸式的趣味聊天
- **情感寄托者**：上传声音，让 AI 模拟语气陪伴交流

## 📋 项目特色

### 🎭 多角色AI对话
- 支持哈利波特、钢铁侠、蜘蛛侠等多个预设角色
- 每个角色具有独特的人格设定和对话风格
- 基于角色设定的个性化回复生成

### 🔊 完整语音交互
- **语音输入**: Whisper API高精度识别
- **智能处理**: GPT-4o-mini + RAG技术增强
- **语音输出**: Edge TTS自然语音合成
- **连续对话**: 支持多轮语音交互

### 🧠 RAG增强对话
- **历史检索**: 基于向量相似度的历史对话检索
- **上下文理解**: 结合历史对话提升回复相关性
- **智能过滤**: 相似度阈值机制避免无关内容
- **个性化体验**: 基于用户历史的个性化回复

### 🔐 完整用户系统
- **安全认证**: python-jose + bcrypt加密
- **权限管理**: 基于用户角色的访问控制
- **会话隔离**: 每个用户独立的会话空间
- **数据安全**: 完整的用户数据保护机制

## 🏗️ 系统架构

### 核心特性
1. **多角色AI对话**: 支持哈利波特、钢铁侠等多个预设角色
2. **语音交互**: 完整的语音输入输出流程
3. **会话管理**: 基于数据库session_id的会话隔离
4. **RAG增强**: 历史对话检索增强生成
5. **用户系统**: 完整的用户注册、登录、权限管理

### 技术架构

```
┌─────────────────┐   基于session_id    ┌─────────────────┐
│   前端 (Vue3)   │ ◄─────────────────► │  后端 (FastAPI) │
│                 │    数据库会话管理    │                 │
│ • 角色选择页    │                      │ • RESTful API   │
│ • 聊天界面      │                      │ • 会话管理      │
│ • 语音交互      │                      │ • 消息处理      │
│ • 用户管理      │                      │ • 用户认证      │
└─────────────────┘                     └─────────────────┘
                                                 │
                                          ┌─────────┼─────────┐
                                          │         │         │
                                     ┌────▼───┐           ┌────▼────┐
                                     │ MySQL  │           │AI服务层 │
                                     │(主数据库+会话)│           │(LLM + RAG + 向量检索)│
                                     └────────┘           │•Whisper │
                                                          │•GPT-4o  │
                                                          │•TTS     │
                                                          │•RAG检索 │
                                                          └─────────┘
```

### 核心技术亮点

#### 1. RAG (检索增强生成) 技术
- **向量嵌入**: 使用Embedding API将历史对话转换为向量
- **相似度检索**: 基于余弦相似度匹配历史对话
- **智能阈值**: 设置0.4相似度阈值，避免不相关内容
- **上下文增强**: 结合历史对话提升AI回复质量

#### 2. 会话管理系统
- **数据库隔离**: 基于session_id的会话数据隔离
- **用户权限**: 用户只能访问自己的会话数据
- **角色绑定**: 每个会话绑定特定AI角色
- **消息追踪**: 完整的消息历史记录和时间戳

#### 3. 语音交互流程
- **语音识别**: Whisper API高精度语音转文字
- **文本处理**: GPT-4o-mini + RAG增强对话生成
- **语音合成**: Edge TTS多语言语音输出
- **实时交互**: 支持连续语音对话

## 🛠️ 技术栈

### 前端技术栈

- **框架**: Vue 3.5.17 + TypeScript
- **UI 组件**: Ant Design Vue 4.2.6 + Element Plus X
- **状态管理**: Pinia 3.0.3
- **路由**: Vue Router 4.5.1
- **样式**: TailwindCSS 4.1.11
- **构建工具**: Vite 7.0.4
- **包管理**: pnpm

### 后端技术栈

- **框架**: FastAPI 0.117.1
- **语言**: Python 3.8+
- **数据库**: MySQL 5.7+/8.0+
- **ORM**: SQLAlchemy 2.0.43
- **会话管理**: 基于数据库session_id隔离
- **认证**: python-jose + bcrypt

### AI 服务

- **LLM**: GPT-4o-mini (阿里云百炼)
- **ASR**: Whisper API
- **TTS**: Edge TTS / ElevenLabs
- **向量化**: text-embedding-v4
- **RAG技术**: 
  - 向量嵌入模型 (Embedding API)
  - 历史对话相似度检索
  - 余弦相似度匹配算法

## 🚀 快速开始

### 环境要求

- Node.js 18+ 和 pnpm
- Python 3.8+
- MySQL 5.7+ 或 8.0+

### 一键启动

```bash
# 1. 克隆项目
git clone <repository-url>
cd cyber-2025

# 2. 启动前端
cd frontend
pnpm i
pnpm run dev

# 3. 启动后端 (新终端)
cd ../backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问地址：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📖 详细安装指南

### 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 开发模式启动
pnpm run dev

# 生产构建
pnpm run build

# 预览构建结果
pnpm run preview
```

### 后端安装

#### 1. Python 环境配置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 数据库配置

**方式一：环境变量配置（推荐）**

```bash
# Windows
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=123456
set DB_NAME=cyber

# Linux/Mac
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=123456
export DB_NAME=cyber
```

**方式二：配置文件修改**
编辑 `app/db/session.py` 文件中的数据库连接参数。

#### 3. AI 服务配置

在 `app/llm/` 目录下创建 `api_keys.json` 文件：

```json
{
  "api_key": "your-api-key-here",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "text-embedding-v4"
}
```

#### 4. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 5. 数据库初始化

```bash
# 方式一：API接口初始化（推荐）
curl -X POST "http://localhost:8000/api/database/init"

# 方式二：访问Swagger UI
# http://localhost:8000/docs#/数据库管理/initialize_database_api_database_init_post
```

## 📚 API 文档

### 接口概览

- **基础地址**: http://localhost:8000
- **文档地址**: http://localhost:8000/docs (Swagger UI)
- **ReDoc 文档**: http://localhost:8000/redoc

### 主要接口模块

#### 1. 数据库管理 `/api/database`

- `POST /api/database/init` - 初始化数据库
- `GET /api/database/test-connection` - 测试连接
- `GET /api/database/status` - 获取状态
- `POST /api/database/reset` - 重置数据库

#### 2. 角色管理 `/api/roles`

- `GET /api/roles/` - 获取角色列表
- `POST /api/roles/` - 创建角色
- `GET /api/roles/{id}` - 获取角色详情
- `PUT /api/roles/{id}` - 更新角色
- `DELETE /api/roles/{id}` - 删除角色

#### 3. 会话管理 `/api/sessions`

- `POST /api/sessions/` - 创建新会话
- `GET /api/sessions/` - 获取会话列表
- `GET /api/sessions/{id}` - 获取会话详情
- `DELETE /api/sessions/{id}` - 删除会话

#### 4. 消息管理 `/api/messages`

- `POST /api/messages/` - 发送消息
- `GET /api/messages/?session_id={id}` - 获取会话消息

#### 5. 用户管理 `/api/users`

- `POST /api/users/` - 创建用户
- `GET /api/users/profile` - 获取用户资料
- `PUT /api/users/profile` - 更新用户资料

## 🗄️ 数据库设计

### 核心表结构

#### 1. 角色表 (roles)

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY COMMENT '角色ID',
    name VARCHAR(50) NOT NULL COMMENT '角色名',
    description TEXT COMMENT '角色描述',
    voice_sample_url VARCHAR(255) COMMENT '声音样本URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. 会话表 (chat_sessions)

```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY COMMENT '会话ID',
    role_id INT NOT NULL COMMENT '角色ID',
    user_id INT COMMENT '用户ID',
    last_message_at TIMESTAMP COMMENT '最近消息时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
```

#### 3. 消息表 (chat_messages)

```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY COMMENT '消息ID',
    session_id INT NOT NULL COMMENT '会话ID',
    role INT NOT NULL COMMENT '角色类型(0-assistant,1-user)',
    query_content TEXT NOT NULL COMMENT '问题内容',
    answer_content TEXT NOT NULL COMMENT '回答内容',
    message_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型',
    metadata JSON COMMENT '消息元数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);
```

## 👥 开发分工

### 前端开发 (Frontend) - 胡世明

**负责模块**:

- 用户界面设计与实现
- 角色选择页面
- 聊天界面开发
- 语音录制与播放
- 状态管理 (Pinia)
- 路由配置

**技术要求**:

- Vue 3 + TypeScript
- 组件化开发
- 响应式设计
- 语音 API 集成

### 后端开发 (Backend) - 李仪静

**负责模块**:

- RESTful API 设计
- 数据库设计与 ORM
- 用户认证与授权
- 会话管理
- AI 服务集成

**技术要求**:

- FastAPI 框架
- SQLAlchemy ORM
- 异步编程

### AI 服务集成 (AI Services) - 张德煜

**负责模块**:

- LLM 模型集成 (GPT-4o-mini)
- 语音识别 (Whisper)
- 语音合成 (TTS)
- 角色人格设计
- 上下文管理

**技术要求**:

- OpenAI API
- 阿里云百炼平台
- 音频处理
- Prompt 工程

### 测试与部署 (DevOps)

**负责模块**:

- 单元测试编写
- 集成测试
- 性能测试
- 部署配置
- 监控告警

**技术要求**:

- pytest 测试框架
- Docker 容器化
- CI/CD 流水线
- 服务器运维

## 📅 项目规划

### 开发周期：5 天

#### Day 1: 框架搭建

- [x] 需求梳理 & 技术选型
- [x] 前后端项目初始化
- [x] 数据库设计
- [x] 基础 API 框架

#### Day 2: 核心功能

- [ ] 前后端 API 对接
- [ ] 角色管理功能
- [ ] 会话创建与管理
- [ ] 基础聊天功能

#### Day 3: AI 集成

- [ ] 语音输入集成 (Whisper)
- [ ] LLM 对话集成 (GPT-4o-mini)
- [ ] 语音输出集成 (TTS)
- [ ] 端到端语音对话

#### Day 4: 优化完善

- [ ] 角色人设 Prompt 优化
- [ ] 短期记忆实现
- [ ] 用户体验优化
- [ ] 错误处理完善

#### Day 5: 测试部署

- [ ] 功能测试
- [ ] 性能优化
- [ ] 文档完善
- [ ] 项目交付

### 功能优先级

#### ✅ 高优先级 (MVP 必须)

- 角色选择 (2-3 个预设角色)
- 语音输入 (ASR)
- AI 文本回复
- 语音输出 (TTS)
- 短记忆 (3-5 轮上下文)

#### ⚖️ 中优先级

- 用户自定义角色
- 更多角色扩展
- 对话历史存档
- 用户账号系统

#### 💤 低优先级

- 群聊/多人互动
- 虚拟形象/动画展示
- 情感识别
- 多语言支持

## 🔧 技术难点

### 1. 高并发会话一致性

**问题**: 多用户同时对话时的会话隔离
**解决方案**:

- session_id 隔离机制
- Redis 存储会话上下文
- 分布式锁防止数据竞争

### 2. 延迟优化

**问题**: 语音链路延迟可能超过 5 秒
**解决方案**:

- 流式 ASR/TTS 处理
- 异步队列优化
- 预加载和缓存机制

### 3. 角色人格保持

**问题**: AI 回复需要保持角色一致性
**解决方案**:

- 系统级 Prompt 设计
- 上下文摘要化
- 角色特征向量化

### 4. 音频处理

**问题**: 实时音频录制与播放
**解决方案**:

- WebRTC 音频 API
- 音频格式转换
- 噪声抑制处理

## 🚀 未来扩展

### 短期扩展 (1-3 个月)

- **更多角色**: 动漫/游戏 IP 角色
- **多技能角色**: 情感识别、任务互动
- **用户系统**: 完整的注册登录体系
- **对话存档**: 长期对话历史管理

### 中期扩展 (3-6 个月)

- **虚拟形象**: WebGL/Unity 3D 渲染
- **多模态交互**: 图像识别与生成
- **社交功能**: 用户间角色分享
- **移动端**: React Native/Flutter 应用

### 长期扩展 (6 个月+)

- **商业化**: 付费角色、高级功能
- **AI 训练**: 用户数据反馈优化
- **生态建设**: 开发者 API 平台
- **国际化**: 多语言、多地区部署

## 🔍 常见问题

### Q: 如何配置 AI 服务密钥？

A: 在 `backend/app/llm/` 目录下创建 `api_keys.json` 文件，填入相应的 API 密钥和配置信息。

### Q: 数据库连接失败怎么办？

A: 检查 MySQL 服务是否启动，确认数据库连接参数正确，可以使用测试接口验证连接。

### Q: 前端代理配置问题？

A: 检查 `vite.config.ts` 中的代理配置，确保 API 路径正确映射到后端服务。

### Q: 语音功能不工作？

A: 确认浏览器支持 WebRTC，检查麦克风权限，验证 AI 服务配置是否正确。

## 📄 许可证

本项目仅用于学习和演示目的。

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

**项目状态**: 🚧 初步完成 | **最后更新**: 2025-09-28
