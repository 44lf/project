from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.correction import Correction, CorrectionUpdate
from app.models.correction import Correction as CorrectionModel
from app.models.user import User as UserModel, UserRole
from app.api.endpoints.auth import get_current_active_user
from app.services.correction_service import correction_service

router = APIRouter()


@router.get("/", response_model=List[Correction])
def get_corrections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取批改列表"""
    if current_user.role == UserRole.STUDENT:
        # 学生只能查看自己的批改
        corrections = db.query(CorrectionModel).join(CorrectionModel.homework).filter(
            CorrectionModel.homework.has(student_id=current_user.id)
        ).offset(skip).limit(limit).all()
    else:
        # 老师和管理员可以查看所有
        corrections = db.query(CorrectionModel).offset(skip).limit(limit).all()
    return corrections


@router.get("/{correction_id}", response_model=Correction)
def get_correction(
    correction_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取批改详情"""
    correction = db.query(CorrectionModel).filter(CorrectionModel.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=404, detail="批改记录不存在")
    
    # 检查权限
    if current_user.role == UserRole.STUDENT:
        if correction.homework.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此批改记录")
    
    return correction


@router.get("/homework/{homework_id}", response_model=Correction)
def get_correction_by_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """根据作业ID获取批改结果"""
    correction = correction_service.get_correction_by_homework(db, homework_id)
    if not correction:
        raise HTTPException(status_code=404, detail="批改记录不存在")
    
    # 检查权限
    if current_user.role == UserRole.STUDENT:
        if correction.homework.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此批改记录")
    
    return correction


@router.post("/{correction_id}/retry")
def retry_correction(
    correction_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """重新批改"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权操作")
    
    correction = db.query(CorrectionModel).filter(CorrectionModel.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=404, detail="批改记录不存在")
    
    try:
        new_correction = correction_service.auto_correct(db, correction.homework_id)
        return {"message": "重新批改成功", "correction": new_correction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批改失败: {str(e)}")
