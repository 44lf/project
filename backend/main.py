from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.database import engine, Base, SessionLocal
from app.api.v1.api import api_router
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def init_db():
    """初始化数据库，创建默认用户"""
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已有用户
        if db.query(User).first():
            return
        
        # 创建默认用户
        default_users = [
            {
                "username": "student1",
                "email": "student1@test.com",
                "full_name": "学生1",
                "role": UserRole.STUDENT,
                "grade": "一年级",
                "class_name": "一班"
            },
            {
                "username": "teacher1",
                "email": "teacher1@test.com",
                "full_name": "教师1",
                "role": UserRole.TEACHER
            },
            {
                "username": "admin",
                "email": "admin@test.com",
                "full_name": "管理员",
                "role": UserRole.ADMIN
            }
        ]
        
        for user_data in default_users:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash("123456"),
                full_name=user_data["full_name"],
                role=user_data["role"],
                grade=user_data.get("grade"),
                class_name=user_data.get("class_name"),
                is_active=True
            )
            db.add(user)
        
        db.commit()
        print("默认用户创建成功！")
    except Exception as e:
        print(f"初始化数据库失败: {e}")
    finally:
        db.close()


# 初始化数据库
init_db()

# 创建上传目录
os.makedirs(os.path.join(settings.UPLOAD_DIR, "homework"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "ocr_results"), exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """根路径"""
    return {
        "message": "欢迎使用K12智能教育平台API",
        "docs": "/docs",
        "version": settings.VERSION
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
