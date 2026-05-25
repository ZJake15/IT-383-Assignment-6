# 🚀 Submission & Deliverables Guide

This guide provides step-by-step instructions to help you complete and compile your submission deliverables for the **AuraGallery** project.

---

## 📂 Deliverables Checklist
1. **GitHub Repository URL**: Direct link to your public or shared GitHub repository.
2. **Live Application URL**: Render deployment link (e.g., `https://auragallery-xyz.onrender.com`).
3. **Compilation Document**: A single PDF or Word document containing the repository link, live URL, and project documentation (screenshots, credentials, and configuration walkthrough).

---

## 1. 🐙 Push Source Code to GitHub

Follow these commands in your terminal to initialize Git and upload your code to GitHub:

```powershell
# 1. Initialize Git in the project root folder
git init

# 2. Create a .gitignore file to exclude virtual environments, cache, and local databases
New-Item -ItemType File -Name .gitignore -Value @"
.venv/
__pycache__/
*.pyc
db.sqlite3
.env
staticfiles/
media/
"@ -Force

# 3. Stage and commit all files
git add .
git commit -m "Initial commit: AuraGallery production-ready release"

# 4. Rename the default branch to main
git branch -M main

# 5. Create a new repository on GitHub, then link it (replace with your actual GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git

# 6. Push to GitHub
git push -u origin main
```

---

## 2. 🚀 Deploy to Render

AuraGallery is pre-configured with a `render.yaml` Blueprint file, which automates the provisioning of both the Web Service and PostgreSQL Database.

### Option A: One-Click Blueprint Deploy (Recommended)
1. Sign in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** at the top right, then select **Blueprint**.
3. Connect your GitHub repository.
4. Render will read `render.yaml` and display the configuration automatically.
5. In the Web Service configuration section, navigate to the **Environment** fields and add your Cloudinary credentials:
   - `CLOUDINARY_CLOUD_NAME` = *[Your Cloudinary Cloud Name]*
   - `CLOUDINARY_API_KEY` = *[Your Cloudinary API Key]*
   - `CLOUDINARY_API_SECRET` = *[Your Cloudinary API Secret]*
6. Click **Deploy**. Render will automatically:
   - Provision a PostgreSQL database.
   - Install dependencies.
   - Collect static assets using WhiteNoise.
   - Run database migrations.
   - Seed the database with default users (`admin`, `user1`, `user2`), categories, and tags.

### Option B: Manual Deploy (Alternative)
If you prefer to configure the services individually:
1. **Database**: Click **New +** -> **PostgreSQL**. Name it and click **Create Database**. Copy the **Internal Database URL**.
2. **Web Service**: Click **New +** -> **Web Service**. Connect your GitHub repository.
   - **Environment**: `Python`
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`
3. **Environment Variables**: In your Web Service settings, add:
   - `DATABASE_URL` = *[Your copied Database URL]*
   - `DEBUG` = `False`
   - `SECRET_KEY` = *[A unique production key]*
   - `CLOUDINARY_CLOUD_NAME` = *[Your Cloudinary Cloud Name]*
   - `CLOUDINARY_API_KEY` = *[Your Cloudinary API Key]*
   - `CLOUDINARY_API_SECRET` = *[Your Cloudinary API Secret]*

---

## 3. 📄 Compile Submission Document

Create a document (PDF or Word) containing the following details to upload to your course portal:

---

### **Submission Cover Sheet**
* **Project Name**: AuraGallery - Photo Album Management System
* **Course ID**: IT 383
* **Student Name**: *[Your Name]*
* **Submission Date**: *[Date]*

---

### **🔗 Live Links**
* **GitHub Repository**: `https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME`
* **Live Deployed App**: `https://YOUR_APP_NAME.onrender.com`

---

### **🔑 Testing & Grading Credentials**
Use the pre-seeded credentials to explore the Role-Based Access Control (RBAC):

* **🔐 Album Administrator**
  - **Username**: `admin`
  - **Password**: `adminpassword123`
  - *Note: Log in with this account to view the security audit logs and console metrics.*

* **👤 Standard User 1**
  - **Username**: `user1`
  - **Password**: `userpassword123`

* **👤 Standard User 2**
  - **Username**: `user2`
  - **Password**: `userpassword123`

---

### **📸 Verification Screens**
Include screenshots of key areas in the document:
1. **Homepage** showing the public gallery grid.
2. **Admin Console** showing security logs (`USER_LOGIN`, etc.).
3. **Album Detail** showing uploaded photos and tags.
