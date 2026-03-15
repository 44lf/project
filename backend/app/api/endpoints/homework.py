import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.config import settings
from app.schemas.homework import Homework, HomeworkCreate
from app.models.homework import Homework as HomeworkModel
from app.models.user import User as UserModel, UserRole
from app.api.endpoints.auth import get_current_active_user
from app.services.correction_service import correction_service

router = APIRouter()


def allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS


@router.post("/upload", response_model=Homework)
async def upload_homework(
    subject: str = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """上传作业"""
    # 检查用户角色
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有学生可以上传作业"
        )
    
    # 检查文件类型
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型"
        )
    
    # 生成唯一文件名
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, "homework", unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过限制"
            )
        buffer.write(content)
    
    # 创建作业记录
    homework = HomeworkModel(
        student_id=current_user.id,
        subject=subject,
        title=title,
        description=description,
        file_path=file_path,
        file_name=file.filename,
        status="processing"  # 异步处理，状态设为processing
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    # 触发自动批改（异步）
    try:
        correction_service.auto_correct(db, homework.id)
    except Exception as e:
        # 记录错误但不影响上传流程
        homework.status = "failed"
        db.commit()
    
    return homework


@router.get("/my", response_model=List[Homework])
def get_my_homework(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取我的作业列表"""
    if current_user.role == UserRole.STUDENT:
        homeworks = db.query(HomeworkModel).filter(
            HomeworkModel.student_id == current_user.id
        ).offset(skip).limit(limit).all()
    else:
        # 老师和管理员可以查看所有作业
        homeworks = db.query(HomeworkModel).offset(skip).limit(limit).all()
    return homeworks


@router.get("/{homework_id}", response_model=Homework)
def get_homework(
    homework_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取作业详情"""
    homework = db.query(HomeworkModel).filter(HomeworkModel.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="作业不存在")
    
    # 检查权限
    if current_user.role == UserRole.STUDENT and homework.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此作业")
    
    return homework
