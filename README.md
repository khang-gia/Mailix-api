# ⚙️ Mailix API (`Mailix-api`)

> **Enterprise Backend API & Real-Time Engine**  
> Built with **Django 4.2**, **Django REST Framework (DRF)**, **Django Channels (WebSockets)**, and **Celery**.

---

## 📖 Overview

**Mailix API (`Mailix-api`)** is the backend application powering the Mailix enterprise workspace platform. It provides a robust, scalable RESTful API and real-time asynchronous communication engine that unifies:

- **Human Resource Management (HRM)**: Employee master profiles, organizational hierarchies, job titles, business units, contracts, insurance, and attendance logs.
- **Customer Relationship Management (CRM)**: Customer and contact directories, Kanban stages, Excel bulk imports, data export, and permanent bulk deletion tasks.
- **Workspace & Task Collaboration**: Task lifecycle management (Kanban/List), sub-work checklists, multi-user assignment, manager tracking, attachments, and threaded comments.
- **Enterprise Social Network**: Internal feeds, rich-text posts, multi-choice polls with live voting, reactions, social groups, and corporate calendar events.
- **Real-Time Push Notifications**: Instant WebSocket messaging powered by Django Channels and Redis for task updates, mentions, and system alerts.
- **Asynchronous Task Processing**: High-throughput file parsing, bulk Excel imports, data cleansing, and background task cancellation via Celery.
- **Multi-Tenant Branding & System Config**: Dynamic company branding (logos, favicons, theme palettes), dynamic app settings, and historical audit trails.

---

## 🏗 Technology Stack

| Component | Technology | Version / Specification |
|---|---|---|
| **Language & Framework** | Python + Django | Python `3.10+` (3.12 recommended), Django `4.2.23` |
| **API Architecture** | Django REST Framework (DRF) | `3.15.2` (JSON REST API + Pagination + Filtering) |
| **Real-Time WebSockets** | Django Channels + Daphne | Channels `4.0.0`, Daphne `4.1.0` (ASGI protocol) |
| **Asynchronous Worker** | Celery + Redis | Celery `5.4.0`, Redis `5.2.1` |
| **Authentication** | JWT (`djangorestframework-simplejwt`) | Access token (7 days), Refresh token (30 days) |
| **Database** | PostgreSQL / SQLite | PostgreSQL (recommended for production), SQLite (dev) |
| **File Parsing & Excel** | openpyxl, xlsxwriter, xlwt | High-speed tabular import/export |
| **Audit Trails** | django-simple-history | `3.7.0` (Row-level change tracking) |
| **Web Server (Prod)** | Gunicorn + Uvicorn Workers | ASGI-ready reverse-proxy worker configuration |

---

## 📂 Project Architecture & Directory Layout

```text
Mailix-api/
├── tttmail/                 # Core Django project configuration
│   ├── asgi.py              # ASGI routing (HTTP + WebSocket Channel router)
│   ├── wsgi.py              # Standard WSGI entry point
│   ├── celery.py            # Celery application initialization & tasks discovery
│   ├── settings.py          # Master settings (Environment variables, DRF, JWT, Channels)
│   ├── urls.py              # Main URL dispatcher (/api/v1/...)
│   └── middlewares/         # Custom middlewares (Channels token authentication)
│
├── core/                    # Core business domain application
│   ├── models.py            # User, ProfileHR, Works, SubWork, Customer, Contact, Notifications
│   ├── views.py             # ViewSets for CRM, HR, Works, Auth & OTP endpoints
│   ├── serializers.py       # DRF ModelSerializers & import validation logic
│   ├── consumers.py         # Django Channels WebSocket NotificationConsumer
│   └── tasks.py             # Scheduled maintenance tasks
│
├── social/                  # Enterprise social networking application
│   ├── models.py            # Post, Comment, Reaction, Poll, Choice, Vote, SocialGroup, Event
│   ├── views.py             # Social feed, group discussions, and interaction ViewSets
│   └── serializers.py       # Serializers for rich-text posts, comments, and poll voting
│
├── system/                  # Organizational structure & tenant settings
│   ├── models.py            # Department, BusinessUnit, SystemGroup, Company
│   ├── views.py             # System configuration, departments, and company theme endpoints
│   └── serializers.py       # Serialization for organizational units & branding
│
├── upload/                  # Asynchronous file processing & bulk operations
│   ├── models.py            # Upload tracking model (progress, status, errors log)
│   ├── tasks.py             # Celery tasks: bulk Excel imports & permanent deletions
│   └── views.py             # File upload & task cancellation endpoints
│
├── timekeeping/             # Employee attendance & timesheet application
│   ├── models.py            # Check-in/check-out logs, timesheet entries
│   └── views.py             # Attendance tracking endpoints
│
├── consult/                 # Consultation workflows & service inquiries
│   ├── models.py            # Consultation requests, stages, and customer notes
│   └── views.py             # Consultation management endpoints
│
├── templates/               # Email and HTML templates (OTP emails, notifications)
├── media/                   # User-uploaded media files (avatars, attachments, imports)
├── staticfiles/             # Collected static files for production delivery
├── logs/                    # Application and worker log files
│
├── manage.py                # Django CLI management entry point
├── start.sh                 # Production ASGI startup script (Gunicorn + Uvicorn)
├── stop.sh                  # Application process termination script
├── background-task.sh       # Background worker management script
└── requirements.txt         # Python package dependencies
```

---

## 🔐 Authentication, Security & Account Lifecycle

### 1. JWT Authentication
- **Token Mechanism**: Powered by `djangorestframework-simplejwt`.
- **Token Lifetime**: Access token valid for **7 days**; Refresh token valid for **30 days**.
- **Handshake Header**: `Authorization: Bearer <access_token>`.

### 2. Multi-Factor & OTP Flows
- **Two-Factor Login / Registration OTP**:
  - `POST /api/v1/auth/otp/generate/`: Generates a numeric OTP sent to the user's registered email.
  - `POST /api/v1/auth/otp/verify/`: Validates the OTP code before granting access tokens.
- **Forgot Password via OTP**:
  - `POST /api/v1/auth/otp/generate_email/`: Sends password reset OTP.
  - `POST /api/v1/auth/reset_password/`: Verifies OTP and applies new password.

### 3. First-Time Login Enforce
- New accounts have `is_first_login = True` on their `ProfileHR`.
- `POST /api/v1/auth/change_password/` handles the mandatory initial password update.

---

## 📡 Real-Time WebSockets (`Django Channels`)

Mailix API uses **Django Channels** and **Redis Channel Layer** to deliver instant real-time events to the frontend.

### 1. Connection Endpoint
```text
ws://<host>:<port>/ws/notifications/?token=<jwt_access_token>
```
*(Also aliased at `/hrm/ws/notifications/` for reverse proxy configurations).*

### 2. Authentication Middleware
The connection handshake is validated by `ChannelsTokenAuthMiddleware`:
- Extracts the token from query parameters (`?token=...`).
- Decodes the JWT payload to populate `scope['user']`.
- Discards invalid or expired connections immediately.

### 3. Notification Routing
Connected clients are subscribed to their unique user group `user_<user_id>`:
- **Work Assignments**: Triggered when a task or sub-work is created or assigned.
- **Status Updates & Comments**: Immediate push when teammates comment on tasks.
- **Upload / Import Progress**: Real-time broadcast when long-running Excel background jobs complete or encounter errors.

---

## ⚡ Background Tasks & Bulk Operations (`Celery`)

Long-running file operations and batch processing are delegated to **Celery** workers with Redis as broker.

### Asynchronous Tasks (`upload/tasks.py`)
1. **Bulk Excel Imports**:
   - `process_import_hr`: Imports employee records, personal data, and direct manager links.
   - `process_import_customer`: Imports corporate/individual customer directories.
   - `process_import_work`: Batch creates tasks with deadlines, assignees, and priorities.
   - `process_import_timekeeping`: Parses daily biometric attendance sheets.
2. **Permanent Bulk Removals (File-Driven)**:
   - `process_remove_hr`: Permanently deletes HR profiles matching unique codes in uploaded Excel files.
   - `process_remove_contact`: Permanently removes contacts by identifier.
   - `process_remove_customer`: Permanently removes customers by unique customer code.
3. **Structured Error Logging**:
   - Errors encountered during row-by-row parsing are stored in `Upload.errors_log` as structured JSON (`{ "type": "not_found", "code": "..." }`), enabling the frontend to translate error logs into any language.
4. **Task Cancellation**:
   - Running jobs can be cancelled via Celery task revocation (`CELERY_DEFAULT_QUEUE`).

---

## 🌐 API Endpoints Reference

All API routes are prefixed under `/api/v1/`:

### Authentication & Account
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login/` | User authentication & JWT pair issuance |
| `POST` | `/auth/logout/` | Invalidate / blacklist session token |
| `POST` | `/auth/refresh/` | Refresh expired access token |
| `POST` | `/auth/register/` | Register new user account |
| `POST` | `/auth/otp/generate/` | Generate OTP for registration or login |
| `POST` | `/auth/otp/generate_email/`| Generate OTP for password recovery |
| `POST` | `/auth/otp/verify/` | Verify OTP code |
| `POST` | `/auth/reset_password/` | Reset password using verified OTP |
| `POST` | `/auth/change_password/` | Change password (first-time login or settings) |

### Human Resources (HRM)
| Method | Endpoint | Description |
|---|---|---|
| `GET, POST` | `/core/profile_hrs/` | Employee profile list & creation |
| `GET, PUT, PATCH, DELETE` | `/core/profile_hrs/{id}/` | Retrieve, update, or remove employee profile |
| `GET` | `/core/hrm_statistic/` | Department headcounts, seniority, and gender metrics |
| `GET, POST` | `/core/titles/` | Job titles and position catalog |
| `GET, POST` | `/system/departments/` | Departments list and organization structure |
| `GET, POST` | `/system/business-units/` | Company business units |

### CRM (Customers & Contacts)
| Method | Endpoint | Description |
|---|---|---|
| `GET, POST` | `/core/customers/` | Customer master directory |
| `GET, PUT, PATCH, DELETE` | `/core/customers/{id}/` | Customer details, status & assignments |
| `GET, POST` | `/core/customer-attachments/`| Customer contract/document attachments |
| `GET, POST` | `/core/customer_comments/` | Customer interaction logs & notes |

### Workspace & Tasks
| Method | Endpoint | Description |
|---|---|---|
| `GET, POST` | `/core/works/` | Task directory (Kanban & List data) |
| `GET, PUT, PATCH, DELETE` | `/core/works/{id}/` | Task details, status, priority, dates |
| `GET, POST` | `/core/work-attachments/` | Task file attachments |
| `GET, POST` | `/core/work_comments/` | Threaded comments on tasks |
| `GET, POST` | `/core/user_notifications/`| User notification feed & mark-as-read |

### Social Network
| Method | Endpoint | Description |
|---|---|---|
| `GET, POST` | `/social/posts/` | Feed posts list and rich-text publication |
| `GET, POST` | `/social/groups/` | Internal social groups |
| `GET, POST` | `/social/interactions/` | Post emoji reactions (Like, Celebrate, etc.) |
| `POST` | `/social/votes/` | Cast votes on post polls |
| `GET, POST` | `/social/post_comments/` | Threaded discussion comments on feed posts |
| `GET, POST` | `/system/schedule-events/` | Corporate event calendar |

### File Uploads & Background Tasks
| Method | Endpoint | Description |
|---|---|---|
| `GET, POST` | `/upload/uploads/` | Submit files for background import/remove |
| `POST` | `/upload/uploads/{id}/cancel/`| Abort ongoing background processing task |

### System & Multi-Tenant Branding
| Method | Endpoint | Description |
|---|---|---|
| `GET, PUT` | `/system/company/` | Company profile, logo, favicon, color themes |
| `GET` | `/system/config/` | Public system configuration |
| `GET` | `/system/admin-config/` | Administrator configuration parameters |

---

## 💻 Environment Variables (`.env`)

Configure the backend via a `.env` file in the `Mailix-api` directory:

```env
# Application Mode
DEBUG=False
SECRET_KEY=change-this-to-a-secure-random-key-in-production

# Database Configuration (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=mailix_db
DB_USER=mailix_user
DB_PASSWORD=your_secure_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Redis & Caches Configuration
CACHE_DEFAULT_LOCATION=redis://127.0.0.1:6379/1
CACHE_HR_LOCATION=redis://127.0.0.1:6379/2
CACHE_CUSTOMER_LOCATION=redis://127.0.0.1:6379/3
CACHE_CONTACT_LOCATION=redis://127.0.0.1:6379/4
CACHE_AUTODIALER_LOCATION=redis://127.0.0.1:6379/5

# Celery Broker & Channels Layer
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer
CHANNEL_LAYERS_CONFIG_HOST=redis://127.0.0.1:6379/2

# Network & Host Security
ALLOWED_HOSTS=localhost,127.0.0.1,api.mailix.vn
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.mailix.vn
CSRF_TRUSTED_ORIGINS=http://localhost:3000,https://app.mailix.vn
COOKIE_SECURE_FLAG=False

# SMTP Email Configuration
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_HOST_USER=your_smtp_username
EMAIL_HOST_PASSWORD=your_smtp_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@mailix.vn

# Static and Media Assets
STATIC_URL=/static/
MEDIA_URL=/media/
APP_NAME_PREFIX=
```

---

## 🚀 Installation & Running

### Prerequisites
- Python `3.10+` (3.12 recommended)
- PostgreSQL Server `14+` (or SQLite for development)
- Redis Server `6.x+` (running on port `6379`)

---

### 1. Environment Setup & Dependency Installation
```bash
cd Mailix-api

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install all required Python packages
pip install -r requirements.txt
```

---

### 2. Database Migrations & Initial Setup
```bash
# Apply all database migrations
python manage.py migrate

# Initialize base system resources (if needed)
python manage.py init_system_resources

# Create administrator account
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic --no-input
```

---

### 3. Running Services

#### A. Development Mode
```bash
# Terminal 1: Run ASGI Server (HTTP & WebSockets)
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Run Celery Worker
celery -A tttmail worker -l info

# Terminal 3: Run Celery Beat (Scheduled tasks)
celery -A tttmail beat -l info
```

#### B. Production Mode
Use the provided shell scripts:

```bash
# Start Gunicorn with Uvicorn ASGI workers (in background)
mkdir -p logs
./start.sh

# Start Celery background task processing
celery -A tttmail worker --loglevel=info --detach --logfile=logs/celery.log

# Stop API server
./stop.sh
```

*(Or direct Gunicorn command)*:
```bash
gunicorn tttmail.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 300 \
  --capture-output \
  --error-logfile logs/error.log \
  --access-logfile logs/access.log \
  -D
```

---

## 🌐 Nginx Reverse Proxy Configuration Example

```nginx
upstream mailix_asgi {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.mailix.vn;

    client_max_body_size 50M;

    # Static and Media files
    location /static/ {
        alias /path/to/Mailix-api/staticfiles/;
    }

    location /media/ {
        alias /path/to/Mailix-api/media/;
    }

    # API Endpoints
    location / {
        proxy_pass http://mailix_asgi;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Real-Time WebSockets
    location /ws/ {
        proxy_pass http://mailix_asgi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## 🛠 Maintenance & Management Commands

| Command | Description |
|---|---|
| `python manage.py migrate` | Apply all database schema changes |
| `python manage.py createsuperuser` | Create an administrative superuser account |
| `python manage.py collectstatic --no-input` | Gather static files into `staticfiles/` |
| `python manage.py init_system_resources` | Populate base system resources |
| `python manage.py shell` | Open interactive Django Python shell |
| `python manage.py check` | Inspect project for configuration and model errors |