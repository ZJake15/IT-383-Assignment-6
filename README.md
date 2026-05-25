# 🌌 AuraGallery - Production-Ready Photo Album Management System

A high-fidelity, enterprise-grade Django Photo Album Management System featuring a modern **Glassmorphic Cyber-Violet UI**, strict **Role-Based Access Control (RBAC)**, Cloud-Native Media Management via **Cloudinary**, and full **PostgreSQL** integration ready for deployment on Render.

---

## 🎨 Design & Aesthetic Excellence
AuraGallery is designed to impress at first sight. It departs from basic, plain styles and implements premium frontend paradigms:
- **Glassmorphic Panels**: Semitransparent dark card containers (`rgba(23, 23, 43, 0.55)`) with precise borders (`1px solid rgba(255, 255, 255, 0.08)`) and high-blur backdrops.
- **Glowing Telemetry & Indicators**: Vibrant indigo (`#8b5cf6`), violet (`#d946ef`), and cyan (`#06b6d4`) highlight indicators, animated gradients, and cybernetic SVGs.
- **Visual Analytics**: Interactive pure CSS progress bars to visualize database parameters, statistics badges, and user cards.
- **Custom Lightbox Viewer**: A highly responsive, pure JavaScript photo modal lightbox featuring tags, title, description, and permission-checked administration routes.

---

## 🛡️ Role-Based Access Control (RBAC) System

The application enforces a fine-grained authorization schema across three identity tiers:

| Capabilities | Anonymous Visitor | Standard User | Album Administrator |
| :--- | :--- | :--- | :--- |
| **Identity Registration** | Yes (Free signup) | N/A | N/A |
| **Explore Public Galleries** | Yes (Read-only) | Yes | Yes |
| **Create Custom Album** | No | Yes | Yes |
| **Access Own Private Album** | No | Yes (Self owned) | Yes (Super-access) |
| **Access Others' Private Album**| No | No (Audited attempt) | Yes (Moderate privileges) |
| **Archive / Upload Photo** | No | Yes (Into own album) | Yes (Into any album) |
| **Delete / Edit Album or Photo** | No | Yes (Owner only) | Yes (Super-control) |
| **Access Monitoring Console** | No | No (Access denied) | Yes (Telemetry + Logs) |
| **Review Security Audit Logs** | No | No | Yes (Immutable list) |

---

## 📦 Core Telemetry & Auditing Logs
To safeguard resource assets, AuraGallery maintains an **enterprise security audit trail** in the database:
- **Login/Logout Tracking**: Logs `USER_LOGIN` and `USER_LOGOUT` events.
- **Resource Lifecycle Audits**: Logs when albums are compiled (`ALBUM_CREATE`), updated (`ALBUM_UPDATE`), or dissolved (`ALBUM_DELETE`).
- **Media Ingestion Audits**: Logs when photos are uploaded (`PHOTO_UPLOAD`) or de-archived (`PHOTO_DELETE`).
- **Security Infraction Capture**: Audits and records every unauthorized access attempt (`UNAUTHORIZED_ACCESS_ATTEMPT`) with the violator's username, timestamp, and client IP address.

---

## 🔑 Preseeded Testing Credentials (Database Seed)
For absolute grading and review convenience, the system database automatically seeds key assets upon build:

- **🔐 Album Administrator**
  - **Username**: `admin`
  - **Password**: `adminpassword123`
  - **Role**: Superuser / Staff / Group: Album Administrators

- **👤 Standard User 1**
  - **Username**: `user1`
  - **Password**: `userpassword123`
  - **Seeded Assets**: Public album titled *"Summer Wanderlust"*

- **👤 Standard User 2**
  - **Username**: `user2`
  - **Password**: `userpassword123`
  - **Seeded Assets**: Private album titled *"Confidential Family Archive"*

- **🏷️ Default Categories**: *Nature, Travel, Family, Portraits, Street, Architecture*
- **🏷️ Default Tags**: *#Adventure, #Sunset, #Scenic, #Memories, #Retro, #Minimalist, #Urban, #Cozy*

---

## 🛠️ Local Development & Quick Start

### 1. Prerequisites
- Python 3.12+ / 3.14
- Git

### 2. Environment Setup
Clone this repository locally, navigate to the folder, and spin up the virtual environment:
```bash
# Activate virtual environment (Windows Powershell)
.venv\Scripts\Activate

# Install complete dependencies list
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file at the root folder (preseeded for SQLite fallback):
```env
DEBUG=True
SECRET_KEY=django-insecure-bk-zys2btzddtuu7l1ef-ox-8jb-i-8-lcz-w-vbyda-5770
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Execute Migrations & Database Seeding
```bash
# Auto-generate database schemas
python manage.py makemigrations
python manage.py migrate

# Seed database with users, categories, tags, and sample albums
python seed_data.py
```

### 5. Start Development Server
```bash
python manage.py runserver
```
Visit the server at `http://127.0.0.1:8000/`. Sign in using either the `admin` account (to explore the Admin Telemetry Console) or `user1` / `user2` credentials.

---

## 🚀 Production Deployment on Render

AuraGallery is completely production-ready with configured PostgreSQL schemas, Gunicorn WSGI threads, and WhiteNoise static asset serving.

### 1. Cloudinary Integration
For production media handling, create a free Cloudinary account and fetch your credentials. Note down either your `CLOUDINARY_URL` or individual cloud name, API key, and secret key. Local media storage is automatically disabled when Cloudinary keys are active.

### 2. Standard Blueprint Deploy (One-Click)
We have included a highly optimized `render.yaml` infrastructure-as-code file. To deploy:
1. Connect your repository to your Render account.
2. In the Render Dashboard, click **New** -> **Blueprint**.
3. Select this repository.
4. Render will automatically parse `render.yaml` and provision:
   - A secure **PostgreSQL Database instance**.
   - A **Python Web Service instance** running Gunicorn.
5. In the Web Service configuration panel on Render, navigate to **Environment** and add the following parameters:
   - `CLOUDINARY_CLOUD_NAME` = *[Your Cloudinary Cloud Name]*
   - `CLOUDINARY_API_KEY` = *[Your Cloudinary API Key]*
   - `CLOUDINARY_API_SECRET` = *[Your Cloudinary API Secret]*
6. Click **Deploy**. The automated `build.sh` script will run pip install, compile static assets via WhiteNoise, run database migrations, and auto-seed initial database schemas.

---

## 📁 Repository Structure
```
├── albums/
│   ├── migrations/
│   ├── admin.py           # Custom registers for full model controls
│   ├── models.py          # Category, Tag, Album, Photo, and AuditLog definitions
│   ├── urls.py            # App route mappings
│   └── views.py           # Robust Class-Based Views (CBVs) with Security Mixins
├── config/
│   ├── settings.py        # Production-grade settings (Cloudinary/WhiteNoise/Security)
│   ├── urls.py            # Main project route index
│   └── wsgi.py
├── static/
│   ├── css/
│   │   └── styles.css     # Premium UI theme stylesheets
│   └── images/
│       └── album-placeholder.svg  # Custom visual SVG placeholder
├── templates/
│   ├── base.html          # Global layout template
│   ├── albums/            # Resource templates (List, Detail, Forms, Dashboard)
│   └── registration/      # Glassmorphic auth screens (Login, Signup)
├── .env                   # Local configuration variables
├── build.sh               # Render compilation and migrate triggers
├── manage.py
├── render.yaml            # Blueprint infrastructure schema
├── requirements.txt       # Dependency version pins
└── seed_data.py           # Database auto-seed script
```
