from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import role, session, message, user, database

app = FastAPI(
    title="AI 角色扮演网站 API",
    description="提供角色管理、会话管理、消息处理等功能的后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(database.router, prefix="/api/database", tags=["数据库管理"])
app.include_router(role.router, prefix="/api/roles", tags=["角色管理"])
app.include_router(session.router, prefix="/api/sessions", tags=["会话管理"])
app.include_router(message.router, prefix="/api/messages", tags=["消息管理"])
app.include_router(user.router, prefix="/api/users", tags=["用户管理"])

@app.get("/")
def read_root():
    """
    根路径，返回API基本信息
    """
    return {
        "message": "AI 角色扮演网站 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "service": "ai-roleplay-api"
    }
