from fastapi import APIRouter, HTTPException, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.ai.request_kimi import RequestKimi

router = APIRouter()

# 初始化 AI 客户端
# 注意：这会在导入时执行，如果环境变量未设置会抛出异常
try:
    kimi = RequestKimi()
except Exception as e:
    print(f"Warning: Failed to initialize AI client: {e}")
    kimi = None

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest,current_user:User=Depends(get_current_user)):
    """
    接收用户消息并获取 AI 回复
    注意：这是一个同步函数，FastAPI 会在线程池中运行它，避免阻塞主事件循环
    """
    if not kimi:
        raise HTTPException(status_code=500, detail="AI client is not initialized")
    
    try:
        reply = kimi.get_response(request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
