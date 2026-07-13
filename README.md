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

## Backend

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/signup` | Register a new user | ❌ |
| POST | `/login` | Authenticate user and return JWT token | ❌ |
| GET | `/protected` | Test protected route | ✅ |

---

### Organizations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/organizations/` | Create a new organization | ✅ |
| GET | `/organizations/` | List all organizations | ❌ |

---

### Projects

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/organizations/{org_id}/projects/` | Create a project inside an organization (Admin only) | ✅ |

---

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/tasks/` | Create a new task | ✅ |
| GET | `/tasks/` | List all tasks (supports sorting) | ✅ |
| GET | `/tasks/{task_id}` | Retrieve a task by ID | ✅ |
| PATCH | `/tasks/{task_id}` | Update task details | ✅ |
| DELETE | `/tasks/{task_id}` | Delete a task | ✅ |
| GET | `/boards/{board_id}/tasks` | Get Kanban board with columns and tasks | ✅ |

**Query Parameters**

| Parameter | Description |
|-----------|-------------|
| `sort_by` | `created_at` or `priority` |
| `order` | `asc` or `desc` |

---

### Comments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/tasks/{task_id}/comments` | Add a comment to a task | ✅ |
| GET | `/tasks/{task_id}/comments` | Retrieve comments for a task | ✅ |
| PATCH | `/tasks/{task_id}/comments/{comment_id}` | Update a comment | ✅ |

---

### Notifications

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/notifications/` | Create a notification | ✅ |
| GET | `/notifications/` | Get all user notifications | ✅ |
| PATCH | `/notifications/{notification_id}/read` | Mark notification as read | ✅ |

---

### Search

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/search?query={keyword}` | Search tasks by title or description across user's organizations | ✅ |

---

## 🔐 Authentication

Protected endpoints require a JWT access token.

After logging in, include the token in the request header:

```http
Authorization: Bearer <your_access_token>
```

---

## 📖 Interactive API Documentation

Once the server is running:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🗄️ Database Schema

DevFlow uses **PostgreSQL** as its primary relational database and **SQLAlchemy ORM** for database interactions. The application follows a modular schema designed to support organizations, projects, Kanban boards, task management, and collaboration.

### Database Technologies

- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Database Driver:** psycopg2
- **Environment Management:** python-dotenv
- **Session Management:** SQLAlchemy SessionLocal

---

## Entity Relationship Overview

```
User
 ├── Membership ───────► Organization
 │                          │
 │                          ▼
 │                      Project
 │                          │
 │                          ▼
 │                        Board
 │                          │
 │                          ▼
 │                     BoardColumn
 │                          │
 │                          ▼
 │                         Task
 │                      ├── Comment
 │                      └── Notification

ActivityLog records actions across organizations.
```

---

## Core Tables

| Table | Description |
|--------|-------------|
| **User** | Stores user credentials and authentication information. |
| **Organization** | Represents a workspace containing multiple projects. |
| **Membership** | Maps users to organizations with role-based permissions (Admin/Member). |
| **Project** | Groups related boards and tasks within an organization. |
| **Board** | Represents a Kanban board for project management. |
| **BoardColumn** | Stores workflow stages such as Todo, In Progress, and Done. |
| **Task** | Contains task details, priority, creator, assignee, and timestamps. |
| **Comment** | Stores comments associated with tasks. |
| **Notification** | Manages user notifications and read status. |
| **ActivityLog** | Records user actions for auditing and activity tracking. |

---

## Relationships

- One **Organization** can contain multiple **Projects**.
- One **Project** can contain multiple **Boards**.
- One **Board** contains multiple **Columns**.
- One **Column** contains multiple **Tasks**.
- One **Task** can have multiple **Comments**.
- Users join organizations through the **Membership** table.
- Users receive task updates through the **Notification** table.
- Important actions are recorded in the **ActivityLog** table.

---

## Database Configuration

The database connection is configured using environment variables.

```env
DATABASE_URL=postgresql://username:password@localhost:5432/devflow
```

SQLAlchemy creates a database engine and manages connections through reusable sessions, ensuring efficient transaction handling and automatic cleanup after each request.

## 🔐 Authentication Flow

DevFlow implements secure authentication using **JWT (JSON Web Tokens)** and **OAuth2 Password Bearer** with password hashing for user credential protection.

### Authentication Workflow

```text
        User
          │
          │ Sign Up
          ▼
  Password Hashing (pwdlib)
          │
          ▼
 PostgreSQL Database
          │
          │ Login
          ▼
Verify Password Hash
          │
          ▼
Generate JWT Access Token
          │
          ▼
Return Bearer Token
          │
          ▼
───────────────────────────────────────
For Protected Requests
───────────────────────────────────────
          │
Authorization: Bearer <JWT>
          │
          ▼
OAuth2PasswordBearer
          │
          ▼
Verify JWT Signature
          │
          ▼
Extract User ID (sub)
          │
          ▼
Fetch User from Database
          │
          ▼
Grant Access to Protected Endpoint
```

---

### Authentication Process

#### 1. User Registration

- User submits email and password.
- Password is securely hashed using **pwdlib** before storage.
- Only the hashed password is stored in PostgreSQL.

#### 2. User Login

- User provides email and password.
- Password is verified against the stored hash.
- If authentication succeeds, a signed JWT access token is generated.

#### 3. JWT Token Generation

The JWT contains:

- **sub** → User ID
- **exp** → Token expiration timestamp

The token is signed using the application's secret key and configured algorithm (HS256).

#### 4. Accessing Protected Routes

For every protected request, the client sends:

```http
Authorization: Bearer <access_token>
```

FastAPI's `OAuth2PasswordBearer` extracts the token, after which the backend:

1. Verifies the JWT signature.
2. Checks whether the token has expired.
3. Extracts the authenticated user's ID (`sub`).
4. Retrieves the user from the database.
5. Grants access if the user exists.

If validation fails, the API returns **401 Unauthorized**.

---

## Security Features

- 🔒 Password hashing using **pwdlib**
- 🔑 JWT-based stateless authentication
- ⏳ Configurable token expiration
- 🛡️ OAuth2 Bearer Token authentication
- 🚫 Protected endpoints require valid JWT
- ⚙️ Secrets managed through environment variables (`.env`)

---

## Environment Variables

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

These variables control JWT signing, verification, and token expiration while keeping sensitive credentials out of the source code.