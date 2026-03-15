from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.user import User as UserModel, UserRole
from app.models.homework import Homework as HomeworkModel
from app.models.correction import Correction as CorrectionModel
from app.api.endpoints.auth import get_current_active_user

router = APIRouter()


@router.get("/student/{student_id}")
def get_student_dashboard(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取学生学情分析"""
    # 检查权限
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="无权访问")
    
    # 获取学生信息
    student = db.query(UserModel).filter(
        UserModel.id == student_id,
        UserModel.role == UserRole.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    # 统计作业数据
    total_homework = db.query(HomeworkModel).filter(
        HomeworkModel.student_id == student_id
    ).count()
    
    completed_homework = db.query(HomeworkModel).filter(
        HomeworkModel.student_id == student_id,
        HomeworkModel.status == "completed"
    ).count()
    
    # 获取平均分数
    avg_score = db.query(func.avg(CorrectionModel.score)).join(HomeworkModel).filter(
        HomeworkModel.student_id == student_id,
        CorrectionModel.score.isnot(None)
    ).scalar() or 0
    
    # 按学科统计
    subject_stats = db.query(
        HomeworkModel.subject,
        func.count(HomeworkModel.id).label("count"),
        func.avg(CorrectionModel.score).label("avg_score")
    ).join(CorrectionModel).filter(
        HomeworkModel.student_id == student_id
    ).group_by(HomeworkModel.subject).all()
    
    # 最近7天提交趋势
    last_7_days = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        count = db.query(HomeworkModel).filter(
            HomeworkModel.student_id == student_id,
            func.date(HomeworkModel.created_at) == date.date()
        ).count()
        last_7_days.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return {
        "student_info": {
            "id": student.id,
            "name": student.full_name,
            "grade": student.grade,
            "class_name": student.class_name
        },
        "overview": {
            "total_homework": total_homework,
            "completed_homework": completed_homework,
            "completion_rate": round(completed_homework / total_homework * 100, 2) if total_homework > 0 else 0,
            "average_score": round(float(avg_score), 2)
        },
        "subject_stats": [
            {
                "subject": stat.subject,
                "count": stat.count,
                "avg_score": round(float(stat.avg_score), 2) if stat.avg_score else 0
            }
            for stat in subject_stats
        ],
        "recent_trend": list(reversed(last_7_days))
    }


@router.get("/class/{class_name}")
def get_class_dashboard(
    class_name: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取班级学情分析"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="无权访问")
    
    # 获取班级学生
    students = db.query(UserModel).filter(
        UserModel.class_name == class_name,
        UserModel.role == UserRole.STUDENT
    ).all()
    
    student_ids = [s.id for s in students]
    
    # 班级整体统计
    total_homework = db.query(HomeworkModel).filter(
        HomeworkModel.student_id.in_(student_ids)
    ).count()
    
    completed_homework = db.query(HomeworkModel).filter(
        HomeworkModel.student_id.in_(student_ids),
        HomeworkModel.status == "completed"
    ).count()
    
    avg_score = db.query(func.avg(CorrectionModel.score)).join(HomeworkModel).filter(
        HomeworkModel.student_id.in_(student_ids),
        CorrectionModel.score.isnot(None)
    ).scalar() or 0
    
    # 按学科统计
    subject_stats = db.query(
        HomeworkModel.subject,
        func.count(HomeworkModel.id).label("count"),
        func.avg(CorrectionModel.score).label("avg_score")
    ).join(CorrectionModel).filter(
        HomeworkModel.student_id.in_(student_ids)
    ).group_by(HomeworkModel.subject).all()
    
    # 学生排名
    student_rankings = db.query(
        UserModel.id,
        UserModel.full_name,
        func.avg(CorrectionModel.score).label("avg_score"),
        func.count(HomeworkModel.id).label("homework_count")
    ).join(HomeworkModel).join(CorrectionModel).filter(
        UserModel.id.in_(student_ids)
    ).group_by(UserModel.id).order_by(func.avg(CorrectionModel.score).desc()).limit(10).all()
    
    return {
        "class_name": class_name,
        "student_count": len(students),
        "overview": {
            "total_homework": total_homework,
            "completed_homework": completed_homework,
            "completion_rate": round(completed_homework / total_homework * 100, 2) if total_homework > 0 else 0,
            "average_score": round(float(avg_score), 2)
        },
        "subject_stats": [
            {
                "subject": stat.subject,
                "count": stat.count,
                "avg_score": round(float(stat.avg_score), 2) if stat.avg_score else 0
            }
            for stat in subject_stats
        ],
        "top_students": [
            {
                "id": s.id,
                "name": s.full_name,
                "avg_score": round(float(s.avg_score), 2) if s.avg_score else 0,
                "homework_count": s.homework_count
            }
            for s in student_rankings
        ]
    }


@router.get("/overview")
def get_overview_dashboard(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取平台概览数据（管理员用）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="无权访问")
    
    # 用户统计
    total_students = db.query(UserModel).filter(UserModel.role == UserRole.STUDENT).count()
    total_teachers = db.query(UserModel).filter(UserModel.role == UserRole.TEACHER).count()
    
    # 作业统计
    total_homework = db.query(HomeworkModel).count()
    pending_homework = db.query(HomeworkModel).filter(HomeworkModel.status == "pending").count()
    completed_homework = db.query(HomeworkModel).filter(HomeworkModel.status == "completed").count()
    
    # 批改统计
    total_corrections = db.query(CorrectionModel).count()
    manual_review_count = db.query(CorrectionModel).filter(
        CorrectionModel.needs_manual_review == 1
    ).count()
    
    # 平均分数
    avg_score = db.query(func.avg(CorrectionModel.score)).filter(
        CorrectionModel.score.isnot(None)
    ).scalar() or 0
    
    return {
        "users": {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_users": total_students + total_teachers
        },
        "homework": {
            "total": total_homework,
            "pending": pending_homework,
            "completed": completed_homework
        },
        "corrections": {
            "total": total_corrections,
            "manual_review_needed": manual_review_count,
            "auto_corrected": total_corrections - manual_review_count
        },
        "average_score": round(float(avg_score), 2)
    }
