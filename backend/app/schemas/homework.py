from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HomeworkBase(BaseModel):
    subject: str
    title: str
    description: Optional[str] = None


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkUpdate(BaseModel):
    subject: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class Homework(HomeworkBase):
    id: int
    student_id: int
    file_path: str
    file_name: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
