# main.py
from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt  # type: ignore[import]
from pydantic import BaseModel
from sqlalchemy import column
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Board, BoardColumn, Comment, DateTime, Notification, Notification, Organization, Membership, Project, Task, User, ActivityLog
from app.schemas import OrganizationCreate, OrganizationResponse, ProjectCreate, ProjectResponse, UserCreate, UserResponse, MembershipCreate, MembershipResponse, TaskCreate, TaskResponse, BoardColumnCreate, BoardColumnResponse, ColumnResponse, BoardTasksResponse, CommentResponse, NotificationResponse, NotificationCreate
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
# Constants (must match values in auth.py)

# OAuth2 scheme for Swagger Authorize popup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded payload:", payload)

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Convert string back to integer
        user_id = int(user_id)

    except JWTError as e:
        print("JWT ERROR:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
# -----------------------------
# Routes
# -----------------------------
@app.post("/signup")
def signup(request: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=request.email, hashed_password=hash_password(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created", "id": new_user.id}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(
    data={"sub": str(user.id)},
    expires_delta=timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected")
def protected(current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello {current_user.email}, you accessed a protected route!"}

@app.post("/organizations/", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_org = Organization(name=org.name, created_by=current_user.id)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    # auto‑assign creator as admin member
    membership = Membership(user_id=current_user.id, organization_id=new_org.id, role="admin")
    db.add(membership)
    db.commit()

    return new_org

@app.get("/organizations/", response_model=List[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(Organization).all()

@app.post("/organizations/{org_id}/projects/", response_model=ProjectResponse)
def create_project(org_id: int, project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = db.query(Membership).filter_by(user_id=current_user.id, organization_id=org_id).first()
    if not membership or membership.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create project in this organization")
    new_project = Project(name=project.name, organization_id=org_id, created_by=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

#CRUD for tasks
@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_task = Task(
        title=task.title,
        description=task.description,
        board_column_id=task.board_column_id,
        priority=task.priority,
        created_by=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_task = db.query(Task).filter(Task.id == task_id).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict(exclude_unset=True).items():
        setattr(existing_task, key, value)
    db.commit()
    db.refresh(existing_task)
    return existing_task

@app.delete("/tasks/{task_id}") 
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"msg": "Task deleted"}

@app.get("/boards/{board_id}/tasks", response_model=BoardTasksResponse)
def get_board_tasks(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    columns = db.query(BoardColumn).filter(BoardColumn.board_id == board_id).all()
    if not columns:
        raise HTTPException(status_code=404, detail="Board not found or has no columns")

    result = {
        "id": board_id,
        "name": columns[0].board.name if columns[0].board else "Unknown Board",
        "columns": []
    }

    for column in columns:
        column_tasks = db.query(Task).filter(Task.board_column_id == column.id).all()
        result["columns"].append({
            "id": column.id,
            "name": column.name,
            "order": column.order,
            "tasks": column_tasks
        })

    return result


@app.get("/tasks/")
def list_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Task)
    if board_id := current_user.board_id:
        query = query.filter(Task.board_column_id == board_id)
    return query.offset(0).limit(100).all()  # Limit to 100 tasks for performance

@app.get("/tasks/", response_model=List[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sort_by: str = "created_at",
    order: str = "desc"
):
    query = db.query(Task)

    if sort_by == "priority":
        query = query.order_by(Task.priority)
    elif sort_by == "created_at":
        query = query.order_by(Task.created_at)

    if order == "asc":
        query = query.order_by(Task.created_at.asc())
    elif order == "desc":
        query = query.order_by(Task.created_at.desc())

    return query.limit(100).all()

@app.post("/tasks/{task_id}/comments", response_model=CommentResponse)
def create_comment(
    task_id: int,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_comment = Comment(
        content=content,
        task_id=task_id,
        user_id=current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@app.get("/tasks/{task_id}/comments", response_model=List[CommentResponse])
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Example authorization: only creator or assignee can view comments
    if task.created_by != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view comments")

    comments = db.query(Comment).filter(Comment.task_id == task_id).all()
    return comments

@app.post("/notifications/", response_model=NotificationResponse)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_notification = Notification(
        user_id=current_user.id,
        content=notification.content,
        read=False,
        created_at=datetime.utcnow()
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


@app.get("/notifications/", response_model=List[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).all()
    return notifications
    
@app.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read = True
    db.commit()
    db.refresh(notification)
    return notification


def notify_user(user_id: int, content: str, db: Session):
    new_notification = Notification(user_id=user_id, content=f"New notification: {content}", read=False, created_at=datetime.utcnow())
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

@app.patch("/tasks/{task_id}/comments/{comment_id}", response_model=CommentResponse)
def update_task_comment(
    task_id: int,
    comment_id: int,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.task_id == task_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this comment")

    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def log_activity(
    organization_id: int,
    user_id: int,
    action: str,
    task_id: int | None,
    db: Session = Depends(get_db)

):
    new_log = ActivityLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        task_id=task_id,
        created_at=datetime.utcnow()
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@app.get("/search/", response_model=List[TaskResponse])
def search_tasks(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all organizations the user belongs to
    memberships = db.query(Membership).filter(Membership.user_id == current_user.id).all()
    if not memberships:
        raise HTTPException(status_code=403, detail="Not authorized to search tasks in any organization")

    org_ids = [m.organization_id for m in memberships]

    # Join through BoardColumn -> Board -> Project to filter by organization
    tasks = (
        db.query(Task)
        .join(BoardColumn, Task.board_column_id == BoardColumn.id)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Project, Board.project_id == Project.id)
        .filter(Project.organization_id.in_(org_ids))
        .filter(
            (Task.title.ilike(f"%{query}%")) |
            (Task.description.ilike(f"%{query}%"))
        )
        .all()
    )

    return tasks




