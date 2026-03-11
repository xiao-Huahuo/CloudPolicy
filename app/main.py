from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from app.api.routes import user, login, ai
from app.services.init_db import init_db_and_admin

# 定义生命周期管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动前执行：初始化数据库和管理员
    init_db_and_admin()
    
    yield
    # 应用关闭后执行：这里暂时没有清理工作

# 将 lifespan 传入 FastAPI
app = FastAPI(lifespan=lifespan)

# 注入路由
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(ai.router, prefix="/ai", tags=["ai","kimi"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    # 传app,且reload=True(热重载),改代码后可以直接改后端,无需重启
    uvicorn.run("app.main:app", host="127.0.0.1", port=8080, reload=True)
