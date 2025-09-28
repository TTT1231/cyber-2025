AI 角色扮演网站 · MVP
一、产品定位

目标
开发一个简洁的 Web 原型，用户能选择角色（如哈利波特 / 蜘蛛侠），并通过语音与其聊天（语音输入 → AI 回复 → 语音输出）。

核心价值
为影视/动漫爱好者、语言学习者、娱乐用户提供沉浸式互动体验。

二、目标用户与用户故事
🎯 目标用户

青少年与二次元/影视爱好者：想和自己喜欢的角色互动。

英语学习者：借助角色扮演提升口语表达。

娱乐用户：想体验沉浸式的趣味聊天。

情感寄托者：上传声音，让 AI 模拟语气陪伴交流。

📖 用户故事

小明（18 岁）：选择哈利波特，用语音问“今天魔法课学什么？”，AI 语音回复。

小红（20 岁）：选择蜘蛛侠，用英文问“Can you teach me some fighting moves?”，AI 用英文语音回答。

章阿姨（45 岁）：上传爷爷的声音样本，AI 模拟爷爷语气与她对话。

三、功能设计与优先级
✅ 高优先级（MVP 必须实现）

角色选择（2~3 个预设角色）

语音输入（ASR）

AI 文本回复

语音输出（TTS）

短记忆（3~5 轮上下文）

⚖️ 中优先级

用户自定义角色（上传声音样本）

更多角色扩展

对话历史存档

用户账号系统

💤 低优先级

群聊 / 多人互动

虚拟形象 / 动画展示

📌 本次开发范围（MVP）： 角色选择 + 语音聊天（输入 + 输出） + 简单记忆

四、技术选型

前端

框架：Vue3 + ElementPlus

功能：角色选择页、聊天界面（文本/语音输入 + 语音输出）

后端

语言：Python（FastAPI）

理由：AI 生态强大（Whisper、TTS、OpenAI SDK）、原型开发快

AI 模型

候选：OpenAI GPT-4o-mini / DeepSeek-R1 / Claude 3.5 Sonnet

选用：GPT-4o-mini（成本低、响应快、生态成熟）

语音模块

ASR：Whisper API

TTS：Edge TTS（免费）或 ElevenLabs（更自然）

五、系统架构
前端（Vue3） → WebSocket / REST API
↓
后端（FastAPI）

1.  接收语音 → Whisper 转文字
2.  调用 GPT-4o-mini → 返回文本
3.  调用 TTS → 返回音频流
4.  Redis 维护短记忆

六、每日任务拆解（5 天）

Day 1：需求梳理 & 技术选型，搭建框架

Day 2：前后端打通 /chat API

Day 3：接入语音输入输出（Whisper + Edge TTS）

Day 4：角色人设 Prompt + 短记忆实现

Day 5：测试 + 文档 + 提交

七、技术难点与亮点

高并发下的会话一致性

类似电商“防止超卖”

方案：session_id 隔离 + Redis 存储最近对话

延迟优化

链路可能 > 5 秒

方案：流式 ASR/TTS + 队列优化

角色人格保持

系统级 Prompt + 上下文摘要化保留角色身份

情感价值扩展

模拟亲人声音，满足情感寄托

八、未来扩展方向

更多角色扩展（动漫/游戏 IP）

多技能角色（情感识别、任务互动）

虚拟形象渲染（WebGL / Unity）

账号系统 + 长期对话存档

九、项目启动说明

## 环境要求

- Python 3.8+
- MySQL 5.7+ 或 8.0+
- pip 包管理器

## 快速启动

### 1. 安装依赖

```bash
# 进入项目目录
cd backend

# 安装Python依赖
pip install -r requirements.txt
# 更新依赖
pip freeze > requirements.txt

# 启动服务
uvicorn app.main:app --reload

# 如果使用虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 数据库配置

#### 方式一：使用环境变量（推荐）

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

#### 方式二：直接修改配置文件

编辑 `app/db/session.py` 文件中的数据库连接参数。

### 3. LLM 模块 API 密钥配置

**重要：** LLM 模块需要 API 密钥才能正常工作。请按以下步骤配置：

#### 创建 API 密钥配置文件

在 `app/llm/` 目录下创建 `api_keys.json` 文件：

```json
{
  "api_key": "your-api-key-here",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "model": "text-embedding-v4"
}
```

#### 配置说明

- **文件位置：** `app/llm/api_keys.json`
- **文件格式：** JSON 格式
- **必填字段：**
  - `api_key`: 阿里云百炼服务的 API 密钥
  - `base_url`: API 服务地址（默认为阿里云百炼兼容模式）
  - `model`: 使用的模型名称

#### 安全注意事项

- 该文件已添加到 `.gitignore` 中，不会被提交到版本控制
- 请妥善保管 API 密钥，不要在代码中硬编码
- 团队成员需要各自创建自己的 `api_keys.json` 文件

#### 支持的功能模块

此配置文件被以下模块使用：

- `embedding_api.py` - 文本向量化
- `llm_api.py` - 大语言模型对话
- `tts_api.py` - 文本转语音
- `fun_asr.py` - 语音识别

### 4. 启动服务

```bash
# 开发模式启动（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式启动
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 验证启动

访问以下地址验证服务启动成功：

- 主页：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## FastAPI 接口查看方法

### 1. Swagger UI 文档（推荐）

启动服务后，访问：http://localhost:8000/docs

功能特点：

- 📖 完整的 API 文档展示
- 🧪 在线接口测试功能
- 📝 请求/响应示例
- 🔍 接口参数详细说明

### 2. ReDoc 文档

访问：http://localhost:8000/redoc

功能特点：

- 📚 更加美观的文档界面
- 📋 结构化的 API 展示
- 🔗 便于分享和查阅

### 3. OpenAPI JSON

访问：http://localhost:8000/openapi.json

- 获取完整的 OpenAPI 规范 JSON 文件
- 可用于生成客户端 SDK

### 4. 命令行查看

```bash
# 查看所有路由
uvicorn app.main:app --reload --log-level info

# 使用curl测试接口
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/api/roles/"
```

## 数据库初始化和迁移操作指南

### 1. 自动初始化（推荐）

#### 使用 API 接口初始化

```bash
# 启动服务后，调用初始化接口
curl -X POST "http://localhost:8000/api/database/init"

# 或在浏览器中访问 Swagger UI 进行操作
# http://localhost:8000/docs#/数据库管理/initialize_database_api_database_init_post
```

#### 初始化内容包括：

- ✅ 自动创建 `cyber` 数据库（如果不存在）
- ✅ 创建所有必要的数据表
- ✅ 插入预设角色数据：
  - 哈利波特（霍格沃茨魔法学校学生）
  - 蜘蛛侠（纽约超级英雄）

### 2. 手动数据库操作

#### 创建数据库

```sql
-- 连接MySQL服务器
mysql -u root -p

-- 创建数据库
CREATE DATABASE cyber CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE cyber;
```

#### 检查数据库状态

```bash
# 测试数据库连接
curl -X GET "http://localhost:8000/api/database/test-connection"

# 查看数据库状态
curl -X GET "http://localhost:8000/api/database/status"
```

### 3. 数据库重置（谨慎操作）

```bash
# 重置数据库（删除所有数据并重新初始化）
curl -X POST "http://localhost:8000/api/database/reset?confirm=true"
```

⚠️ **注意事项：**

- 重置操作会删除所有现有数据
- 生产环境请谨慎使用
- 建议在重置前备份重要数据

### 4. 数据库迁移

#### 表结构变更

当模型文件发生变化时：

1. 修改 `app/models/` 目录下的模型文件
2. 重启服务，SQLAlchemy 会自动检测变更
3. 或调用初始化接口重新创建表结构

#### 数据备份与恢复

```bash
# 备份数据库
mysqldump -u root -p cyber > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
mysql -u root -p cyber < backup_20240101_120000.sql
```

### 5. 常见问题排查

#### 连接失败

```bash
# 检查MySQL服务状态
# Windows
net start mysql

# Linux
sudo systemctl status mysql
sudo systemctl start mysql
```

#### 权限问题

```sql
-- 创建用户并授权
CREATE USER 'cyber_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cyber.* TO 'cyber_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 编码问题

确保数据库和表都使用 `utf8mb4` 编码：

```sql
ALTER DATABASE cyber CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

📌 总结

目标：5 天内交付「角色选择 + 语音对话」完整原型

技术亮点：高并发会话一致性、延迟优化、角色人格保持

🗄️ 数据库设计（MVP 范围）

MVP 不需要复杂账号系统，核心表：角色 / 会话 / 消息

1. 角色表（roles）
   CREATE TABLE roles (
   id SERIAL PRIMARY KEY COMMENT '角色 id',
   name VARCHAR(50) NOT NULL COMMENT '角色名',
   description TEXT COMMENT '角色描述',
   voice_sample_url VARCHAR(255) COMMENT '声音样本（可选）',
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
   );

2. 会话表（chat_sessions）
   CREATE TABLE chat_sessions (
   id SERIAL PRIMARY KEY COMMENT '会话 id',
   role_id INT NOT NULL COMMENT '角色 id',
   last_message_at TIMESTAMP COMMENT '最近一次对话时间',
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
   FOREIGN KEY (role_id) REFERENCES roles(id)
   );

3. 消息表（chat_messages）
   CREATE TABLE chat_messages (
   id SERIAL PRIMARY KEY COMMENT '消息 id',
   session_id INT NOT NULL COMMENT '会话 id',
   role INT NOT NULL COMMENT '0-assistant,1-user',
   content TEXT NOT NULL COMMENT '消息内容',
   message_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型，文本/音频等',
   metadata JSON COMMENT '消息元数据（如音频 URL/时长/格式）',
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
   FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
   );

🌐 API 设计（MVP 范围）

## 完整 API 接口列表

### 1. 数据库管理接口 `/api/database`

- `POST /api/database/init` → 初始化数据库和基础数据
- `GET /api/database/test-connection` → 测试数据库连接
- `GET /api/database/status` → 获取数据库状态信息
- `POST /api/database/reset` → 重置数据库（需确认）

### 2. 角色接口 `/api/roles`

- `POST /api/roles/` → 创建角色
- `GET /api/roles/` → 获取角色列表
- `GET /api/roles/{id}` → 获取角色详情
- `PUT /api/roles/{id}` → 更新角色
- `DELETE /api/roles/{id}` → 删除角色
- `GET /api/roles/system/roles` → 获取系统预设角色

### 3. 会话接口 `/api/sessions`

- `POST /api/sessions/` → 创建新会话（选择一个角色）
- `GET /api/sessions/` → 获取所有会话列表
- `GET /api/sessions/{id}` → 获取会话详情
- `DELETE /api/sessions/{id}` → 删除会话

### 4. 消息接口 `/api/messages`

- `POST /api/messages/` → 发送消息
  - 入参：session_id, role, content, message_type, metadata
  - 出参：存储消息记录（含 AI 回复）
- `GET /api/messages/?session_id={id}` → 获取某会话的所有消息

### 5. 用户接口 `/api/users`

- `POST /api/users/` → 创建用户
- `GET /api/users/` → 获取用户列表
- `GET /api/users/{id}` → 获取用户详情
- `PUT /api/users/{id}` → 更新用户信息
- `DELETE /api/users/{id}` → 删除用户

### 6. 系统接口

- `GET /` → API 基本信息
- `GET /health` → 健康检查
