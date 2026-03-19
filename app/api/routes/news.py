import asyncio
from fastapi import APIRouter, Query
from app.services.news_crawler import (
    get_hot_news, get_central_docs, get_hot_keywords,
    search_news, get_news_with_images, get_daily_gov_summary
)

router = APIRouter()

async def _run(func, *args, fallback=None):
    """在线程池中运行同步爬虫，超时返回 fallback"""
    try:
        loop = asyncio.get_event_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(None, func, *args),
            timeout=8.0
        )
    except Exception as e:
        return fallback

@router.get("/hot")
async def hot_news(limit: int = 10):
    items = await _run(get_hot_news, limit, fallback=[])
    return {"items": items or []}

@router.get("/central-docs")
async def central_docs(limit: int = 5):
    items = await _run(get_central_docs, limit, fallback=[])
    return {"items": items or []}

@router.get("/keywords")
async def hot_keywords():
    items = await _run(get_hot_keywords, fallback=[])
    return {"items": items or []}

@router.get("/search")
async def news_search(q: str = Query("", description="搜索关键词"), limit: int = 20):
    items = await _run(search_news, q, limit, fallback=[])
    return {"items": items or [], "query": q}

@router.get("/with-images")
async def news_with_images(limit: int = 5):
    items = await _run(get_news_with_images, limit, fallback=[])
    return {"items": items or []}

@router.get("/daily-summary")
async def daily_summary():
    result = await _run(get_daily_gov_summary, fallback={})
    return result or {}
