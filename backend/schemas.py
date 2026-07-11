from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str   

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    created_by: Optional[int]
    created_at: Optional[datetime]

    
    members: List[UserResponse] = []

    class Config:
        orm_mode = True

class MembershipBase(BaseModel):
    role: Optional[str] = "member"

class MembershipCreate(MembershipBase):
    user_id: int
    organization_id: int

class MembershipResponse(MembershipBase):
    id: int
    user_id: int
    organization_id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class BoardColumnCreate(BaseModel):
    name: str
    board_id: int
    order: Optional[int] = 0

class BoardColumnResponse(BaseModel):
    id: int
    name: str
    board_id: int
    order: Optional[int] = 0

    class Config:
        orm_mode = True

class BoardCreate(BaseModel):
    name: str
    project_id: int

class BoardResponse(BaseModel):
    id: int
    name: str
    project_id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class ProjectCreate(BaseModel):
    name: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    organization_id: int
    created_by: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    board_column_id: int
    priority: Optional[int] = 1

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    board_column_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[str] = None
    created_by: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True   # replaces orm_mode in Pydantic v2


class ColumnResponse(BaseModel):
    id: int
    name: str
    order: int
    tasks: List[TaskResponse]

    class Config:
        from_attributes = True

class BoardTasksResponse(BaseModel):
    id: int
    name: str
    columns: List[ColumnResponse]

    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


    class Config:
        orm_mode = True

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    content: str
    read: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class NotificationCreate(BaseModel):
    content: str

class ActivityLogResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    action: str
    task_id: Optional[int] = None
    created_at: Optional[datetime]

    class Config:
        orm_mode = True