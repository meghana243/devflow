from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

class Membership(Base): 
    __tablename__ = "memberships"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    role = Column(String, default="member")
    created_at = Column(DateTime)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime)
    board_id=Column(Integer, ForeignKey("boards.id"))
    organizations = relationship("Organization", secondary="memberships", backref="members")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)
    boards = relationship("Board", backref="project")

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))


    # One board has many columns
    columns = relationship("BoardColumn", back_populates="board")

class BoardColumn(Base):
    __tablename__ = "board_columns"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    order = Column(Integer)
    board_id = Column(Integer, ForeignKey("boards.id"))

    # Link back to Board
    board = relationship("Board", back_populates="columns")

    # One column has many tasks
    tasks = relationship("Task", back_populates="column")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    board_column_id = Column(Integer, ForeignKey("board_columns.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    priority = Column(String)
    due_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Link back to BoardColumn
    column = relationship("BoardColumn", back_populates="tasks")

class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))

class TaskLabel(Base):
    __tablename__ = "task_labels"
    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    label_id = Column(Integer, ForeignKey("labels.id"), primary_key=True)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String, nullable=False)
    read = Column(Boolean, default=False)  # False for unread, True for read
    created_at = Column(DateTime)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime)