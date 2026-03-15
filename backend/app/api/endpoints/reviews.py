from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.review import ManualReview, ManualReviewCreate, ManualReviewUpdate
from app.models.review import ManualReview as ManualReviewModel
from app.models.correction import Correction as CorrectionModel
from app.models.user import User as UserModel, UserRole
from app.api.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/pending", response_model=List[ManualReview])
def get_pending_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取待审核列表"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权访问")
    
    reviews = db.query(ManualReviewModel).filter(
        ManualReviewModel.status == "pending"
    ).offset(skip).limit(limit).all()
    return reviews


@router.get("/", response_model=List[ManualReview])
def get_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取所有审核记录"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权访问")
    
    reviews = db.query(ManualReviewModel).offset(skip).limit(limit).all()
    return reviews


@router.get("/{review_id}", response_model=ManualReview)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取审核详情"""
    review = db.query(ManualReviewModel).filter(ManualReviewModel.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="审核记录不存在")
    
    if current_user.role == UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="无权访问")
    
    return review


@router.post("/{correction_id}/review", response_model=ManualReview)
def create_review(
    correction_id: int,
    review_data: ManualReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """创建人工审核"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权操作")
    
    # 检查批改记录是否存在
    correction = db.query(CorrectionModel).filter(CorrectionModel.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=404, detail="批改记录不存在")
    
    # 创建审核记录
    review = ManualReviewModel(
        correction_id=correction_id,
        reviewer_id=current_user.id,
        score=review_data.score,
        feedback=review_data.feedback,
        review_notes=review_data.review_notes,
        status="approved"
    )
    
    db.add(review)
    
    # 更新批改记录状态
    correction.status = "manual_reviewed"
    correction.score = review_data.score
    if review_data.feedback:
        correction.feedback = review_data.feedback
    
    db.commit()
    db.refresh(review)
    return review


@router.put("/{review_id}", response_model=ManualReview)
def update_review(
    review_id: int,
    review_data: ManualReviewUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """更新审核记录"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权操作")
    
    review = db.query(ManualReviewModel).filter(ManualReviewModel.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="审核记录不存在")
    
    # 只能修改自己的审核记录，除非是管理员
    if current_user.role != UserRole.ADMIN and review.reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己的审核记录")
    
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    return review
