import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.opinion import Opinion
from app.models.policy_document import PolicyDocument, DocStatus
from app.models.user import User

logger = logging.getLogger(__name__)
from app.schemas.opinion import OpinionCreate, OpinionOut

router = APIRouter()


def _opinion_to_out(op: Opinion, session: Session) -> OpinionOut:
    user = session.get(User, op.user_id)
    return OpinionOut(**op.model_dump(), user_name=user.uname if user else None)


# 提交评议（登录用户）
@router.post("/", response_model=OpinionOut)
def create_opinion(
    op_in: OpinionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    doc = session.get(PolicyDocument, op_in.doc_id)
    if not doc or doc.status != DocStatus.approved:
        raise HTTPException(status_code=404, detail="政策文件不存在或未审核通过")
    op = Opinion(**op_in.model_dump(), user_id=current_user.uid)
    session.add(op)
    session.commit()
    session.refresh(op)
    logger.info(f"用户 {current_user.uid} 提交评议 doc={op_in.doc_id}")
    return _opinion_to_out(op, session)


# 获取某文件的评议列表（公开）
@router.get("/doc/{doc_id}", response_model=List[OpinionOut])
def list_opinions_by_doc(
    doc_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    ops = session.exec(
        select(Opinion).where(Opinion.doc_id == doc_id)
        .order_by(Opinion.created_time.desc())
        .offset(skip).limit(limit)
    ).all()
    return [_opinion_to_out(op, session) for op in ops]


# 获取全站最新评议（民意大厅公开信息流）
@router.get("/feed", response_model=List[OpinionOut])
def opinion_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    ops = session.exec(
        select(Opinion).order_by(Opinion.created_time.desc())
        .offset(skip).limit(limit)
    ).all()
    return [_opinion_to_out(op, session) for op in ops]


# 认证主体查看自己文件的评议
@router.get("/mine", response_model=List[OpinionOut])
def my_doc_opinions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from app.models.user import UserRole
    if current_user.role not in (UserRole.certified, UserRole.admin):
        raise HTTPException(status_code=403, detail="需要认证主体权限")
    my_doc_ids = session.exec(
        select(PolicyDocument.id).where(PolicyDocument.uploader_id == current_user.uid)
    ).all()
    if not my_doc_ids:
        return []
    ops = session.exec(
        select(Opinion).where(Opinion.doc_id.in_(my_doc_ids))
        .order_by(Opinion.created_time.desc())
    ).all()
    return [_opinion_to_out(op, session) for op in ops]


# 评议点赞
@router.post("/{opinion_id}/like")
def like_opinion(opinion_id: int, session: Session = Depends(get_session)):
    op = session.get(Opinion, opinion_id)
    if not op:
        raise HTTPException(status_code=404, detail="评议不存在")
    op.like_count += 1
    session.add(op)
    session.commit()
    return {"like_count": op.like_count}
