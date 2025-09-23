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

小明（18岁）：选择哈利波特，用语音问“今天魔法课学什么？”，AI 语音回复。

小红（20岁）：选择蜘蛛侠，用英文问“Can you teach me some fighting moves?”，AI 用英文语音回答。

章阿姨（45岁）：上传爷爷的声音样本，AI 模拟爷爷语气与她对话。

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
   1. 接收语音 → Whisper 转文字
   2. 调用 GPT-4o-mini → 返回文本
   3. 调用 TTS → 返回音频流
   4. Redis 维护短记忆

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

九、运行说明
# 安装依赖
pip install -r requirements.txt

# 更新依赖
pip freeze > requirements.txt

# 启动服务
uvicorn app.main:app --reload

📌 总结

目标：5 天内交付「角色选择 + 语音对话」完整原型

技术亮点：高并发会话一致性、延迟优化、角色人格保持

🗄️ 数据库设计（MVP 范围）

MVP 不需要复杂账号系统，核心表：角色 / 会话 / 消息

1. 角色表（roles）
CREATE TABLE roles (
    id SERIAL PRIMARY KEY COMMENT '角色id',
    name VARCHAR(50) NOT NULL COMMENT '角色名',
    description TEXT COMMENT '角色描述',
    voice_sample_url VARCHAR(255) COMMENT '声音样本（可选）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);

2. 会话表（chat_sessions）
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY COMMENT '会话id',
    role_id INT NOT NULL COMMENT '角色id',
    last_message_at TIMESTAMP COMMENT '最近一次对话时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

3. 消息表（chat_messages）
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY COMMENT '消息id',
    session_id INT NOT NULL COMMENT '会话id',
    role INT NOT NULL COMMENT '0-assistant,1-user',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型，文本/音频等',
    metadata JSON COMMENT '消息元数据（如音频URL/时长/格式）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

🌐 API 设计（MVP 范围）
1. 角色接口 /roles

POST /roles → 创建角色

GET /roles → 获取角色列表

GET /roles/{id} → 获取角色详情

PUT /roles/{id} → 更新角色

DELETE /roles/{id} → 删除角色

2. 会话接口 /sessions

POST /sessions → 创建新会话（选择一个角色）

GET /sessions → 获取所有会话列表

GET /sessions/{id} → 获取会话详情

DELETE /sessions/{id} → 删除会话

3. 消息接口 /messages

POST /messages
入参：session_id, role, content, message_type, metadata
出参：存储消息记录（含 AI 回复）

GET /messages?session_id={id} → 获取某会话的所有消息