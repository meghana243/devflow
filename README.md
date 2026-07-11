### DEVFLOW 

# DevFlow Backend

DevFlow is a FastAPI-based backend for managing organizations, projects, boards, columns, and tasks.  
It supports authentication, role-based access, and task search across organizations.

---

## 🚀 Features
- **Authentication**: JWT-based login and user management.
- **Organizations & Memberships**: Users belong to organizations via memberships.
- **Projects & Boards**: Projects are scoped to organizations; boards belong to projects.
- **Board Columns & Tasks**: Kanban-style task management with priorities and assignees.
- **Search**: Full-text search across tasks, scoped to user’s organization memberships.
- **Swagger UI**: Auto-generated API docs at `/docs`.

---

## 🛠️ Tech Stack
- **FastAPI** (web framework)
- **SQLAlchemy** (ORM)
- **Alembic** (migrations)
- **PostgreSQL** (database)
- **JWT Authentication**